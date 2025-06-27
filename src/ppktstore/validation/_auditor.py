import abc
import typing
from ..model import PhenopacketStore
from stairval import Auditor
from stairval.notepad import Notepad
from phenosentry.validation import get_cohort_auditor
from phenosentry.model import CohortAuditor

class PhenopacketStoreAuditor(Auditor[PhenopacketStore], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def make_id(self) -> str:
        """
        Get a `str` with the auditor id.
        """
        pass


class DefaultPhenopacketStoreAuditor(PhenopacketStoreAuditor):

    def __init__(
        self,
        checks: typing.Iterable[PhenopacketStoreAuditor],
    ):
        self._checks = tuple(checks)
        self._id = '[' + ', '.join(check.make_id() for check in self._checks) + ']'

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad,
    ):
        for cohort in item.cohorts():
            cohort_pad = notepad.add_subsection(cohort.name)
            for check in self._checks:
                if isinstance(check, CohortAuditor):
                    check.audit(
                        item=cohort,
                        notepad=cohort_pad,
                    )

    def make_id(self) -> str:
        return self._id

def default_auditor() -> PhenopacketStoreAuditor:
    checks = (
       get_cohort_auditor()
    )
    return DefaultPhenopacketStoreAuditor(checks=checks)