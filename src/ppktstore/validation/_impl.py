import io
import logging
import typing

import hpotk

from phenosentry.auditor import PhenopacketAuditor, CohortAuditor
from phenosentry.auditor.phenopacket import (
    NoUnwantedCharactersAuditor,
    DeprecatedTermIdAuditor,
    PhenotypicAbnormalityAuditor,
    PresentAnnotationPropagationAuditor,
    ExcludedAnnotationPropagationAuditor,
    AnnotationInconsistencyAuditor,
)
from phenosentry.auditor.cohort import UniqueIdsAuditor
from stairval import Auditor
from stairval.notepad import Notepad

from ..model import PhenopacketStore


class PhenopacketStoreAuditor(Auditor[PhenopacketStore]):
    """
    Apply a sequence of cohort checks followed by checks of the individual phenopackets.
    """

    def __init__(
        self,
        cohort_auditors: typing.Iterable[CohortAuditor],
        phenopacket_auditors: typing.Iterable[PhenopacketAuditor],
    ):
        self._cohort_auditors = tuple(cohort_auditors)
        self._pp_auditors = tuple(phenopacket_auditors)

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad,
    ):
        for cohort in item.cohorts():
            cohort_pad = notepad.add_subsection(cohort.name)
            ps_cohort = cohort.cohort

            # Start with cohort checks ...
            for auditor in self._cohort_auditors:
                auditor.audit(ps_cohort, cohort_pad)

            # ... and follow with checks on the phenopacket level.
            for auditor in self._pp_auditors:
                for i, pp in enumerate(ps_cohort.members):
                    pp_pad = cohort_pad.add_subsection(i)
                    auditor.audit(pp, pp_pad)


def make_phenopacket_store_auditor(
    hpo: hpotk.MinimalOntology,
) -> PhenopacketStoreAuditor:
    """
    Default auditor checks that each phenopacket meets the criteria of the following auditors:

    * :class:`phenosentry.auditor.phenopacket.NoUnwantedCharactersAuditor`
    * :class:`phenosentry.auditor.phenopacket.DeprecatedTermIdAuditor`
    * :class:`phenosentry.auditor.phenopacket.PhenotypicAbnormalityAuditor`
    * :class:`phenosentry.auditor.phenopacket.PresentAnnotationPropagationAuditor`
    * :class:`phenosentry.auditor.phenopacket.ExcludedAnnotationPropagationAuditor`
    * :class:`phenosentry.auditor.phenopacket.AnnotationInconsistencyAuditor`

    Additionally, the cohorts must satisfy:

    * :class:`phenosentry.auditor.cohort.UniqueIdsAuditor`
    """
    cohort_auditors = [
        UniqueIdsAuditor(),
    ]

    phenopacket_auditors = [
        NoUnwantedCharactersAuditor.no_whitespace(),
        DeprecatedTermIdAuditor(hpo),
        PhenotypicAbnormalityAuditor(hpo),
        PresentAnnotationPropagationAuditor(hpo),
        ExcludedAnnotationPropagationAuditor(hpo),
        AnnotationInconsistencyAuditor(hpo),
    ]

    return PhenopacketStoreAuditor(
        cohort_auditors=cohort_auditors,
        phenopacket_auditors=phenopacket_auditors,
    )


def qc_phenopacket_store(
    store: PhenopacketStore,
    hpo: hpotk.MinimalOntology,
    logger: logging.Logger,
) -> int:
    logger.info("Checking phenopacket store")
    auditor = make_phenopacket_store_auditor(hpo)
    notepad = auditor.prepare_notepad(store.name)
    auditor.audit(
        item=store,
        notepad=notepad,
    )

    buf = io.StringIO()
    notepad.summarize(file=buf)
    if notepad.has_errors_or_warnings(include_subsections=True):
        logger.error(buf.getvalue())
        return 1
    else:
        logger.info(buf.getvalue())
        return 0
