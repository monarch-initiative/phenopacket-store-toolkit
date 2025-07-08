import dataclasses
import typing
from .phenopacket_info import PhenopacketInfo
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket

@dataclasses.dataclass
class CohortInfo:
    """
    Represents information about a cohort of phenopackets.

    Attributes:
        name (str): The name of the cohort.
        path (str): The file path to the cohort directory or file.
        phenopackets (typing.Collection[PhenopacketInfo]): A collection of PhenopacketInfo objects representing the phenopackets in the cohort.
    """
    name: str
    path: str
    phenopackets: typing.Collection[PhenopacketInfo]

    def iter_phenopackets(self) -> typing.Iterator[Phenopacket]:
        return map(lambda pi: pi.phenopacket, self.phenopackets)

    def __len__(self) -> int:
        return len(self.phenopackets)