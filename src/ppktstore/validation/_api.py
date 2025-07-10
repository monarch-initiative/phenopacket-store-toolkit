import abc
from ..model import PhenopacketStore
from stairval import Auditor

class PhenopacketStoreAuditor(Auditor[PhenopacketStore], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def id(self) -> str:
        """
        Get a `str` with the auditor id.
        """
        pass