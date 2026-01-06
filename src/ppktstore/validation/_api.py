import abc

from stairval import Auditor

from ..model import PhenopacketStore


class PhenopacketStoreAuditor(Auditor[PhenopacketStore], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def id(self) -> str:
        """
        Get a `str` with the auditor id.
        """
        pass
