import abc

from ppktstore.model import PhenopacketStore
from stairval import Auditor


class PhenopacketStoreAuditor(Auditor[PhenopacketStore], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def make_id(self) -> str:
        """
        Get a `str` with the auditor id.
        """
        pass
