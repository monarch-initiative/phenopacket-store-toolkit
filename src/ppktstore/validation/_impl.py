from ..model import PhenopacketStore
from ._api import PhenopacketStoreAuditor
import logging
import io
import typing
from stairval.notepad import Notepad
from phenosentry.validation import get_cohort_auditor
from phenosentry.validation import CohortAuditor
from phenopackets.schema.v2.phenopackets_pb2 import Cohort
from ._checks import UniquePhenopacketId

class DefaultPhenopacketStoreAuditor(PhenopacketStoreAuditor):

    def __init__(
        self,
        checks: typing.Iterable[PhenopacketStoreAuditor | CohortAuditor],
    ):
        self._checks = tuple(checks)
        self._id = '[' + ', '.join(check.id() for check in self._checks) + ']'

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad,
    ):

        for check in self._checks:
            if isinstance(check, CohortAuditor):
                for cohort in item.cohorts():
                    cohort_pad = notepad.add_subsection(cohort.name)
                    phenopackets = [p.phenopacket for p in cohort.phenopackets]
                    check.audit(
                        item=Cohort(id=cohort.name, members=phenopackets),
                        notepad=cohort_pad,
                    )
            else:
                check.audit(
                    item=item,
                    notepad=notepad,
                )

    def id(self) -> str:
        return self._id

def default_auditor() -> PhenopacketStoreAuditor:
    checks = [
        UniquePhenopacketId(),
        get_cohort_auditor()
    ]
    return DefaultPhenopacketStoreAuditor(checks=checks)

def qc_phenopacket_store(
    store: PhenopacketStore,
    logger: logging.Logger
) -> int:
    logger.info('Checking phenopacket store')
    auditor = default_auditor()
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