import abc

from ppktstore.model import PhenopacketStore
from stairval import Auditor


class PhenopacketStoreAuditor(Auditor[PhenopacketStore], metaclass=abc.ABCMeta):
    pass
