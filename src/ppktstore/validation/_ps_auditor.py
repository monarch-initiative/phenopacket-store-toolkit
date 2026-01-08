import typing

import hpotk

from phenosentry.auditor import PhenopacketAuditor, CohortAuditor
from phenosentry.auditor.phenopacket import (
    NoUnwantedCharactersAuditor,
    HpoTermIsDefinedAuditor,
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

    @staticmethod
    def default_auditor(
        hpo: hpotk.MinimalOntology,
    ) -> "PhenopacketStoreAuditor":
        """
        The default auditor checks that each phenopacket meets the criteria of the following auditors:

        * :class:`phenosentry.auditor.phenopacket.NoUnwantedCharactersAuditor`
        * :class:`phenosentry.auditor.phenopacket.HpoTermIsDefinedAuditor`
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
            HpoTermIsDefinedAuditor(hpo),
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
