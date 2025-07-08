import pathlib
from abc import ABCMeta, abstractmethod
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket
from google.protobuf.json_format import Parse
import zipfile

class PhenopacketInfo(metaclass=ABCMeta):
    """
     Abstract base class representing phenopacket information.

     Properties:
         path (str): The file path to the phenopacket.
         phenopacket (Phenopacket): The parsed phenopacket object.
     """

    @property
    @abstractmethod
    def path(self) -> str:
        pass

    @property
    @abstractmethod
    def phenopacket(self) -> Phenopacket:
        pass

class EagerPhenopacketInfo(PhenopacketInfo):
    """
    Represents phenopacket information that is eagerly loaded into memory.

    Methods:
        from_path(path: str) -> PhenopacketInfo: Creates an instance from a file path.
        from_phenopacket(path: str, pp: Phenopacket) -> PhenopacketInfo: Creates an instance from a file path and a Phenopacket object.
    """

    @staticmethod
    def from_path(path: pathlib.Path) -> PhenopacketInfo:
        pp = Parse(path.read_text(), Phenopacket())
        return EagerPhenopacketInfo.from_phenopacket(str(path), pp)

    @staticmethod
    def from_phenopacket(path: str, pp: Phenopacket) -> PhenopacketInfo:
        return EagerPhenopacketInfo(path, pp)

    def __init__(self, path: str, phenopacket: Phenopacket):
        self._path = path
        self._phenopacket = phenopacket

    @property
    def path(self) -> str:
        return self._path

    @property
    def phenopacket(self) -> Phenopacket:
        return self._phenopacket

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, EagerPhenopacketInfo)
            and self._path == value._path
            and self._phenopacket == value._phenopacket
        )

    def __hash__(self) -> int:
        return hash((self._path, self._phenopacket))

    def __str__(self) -> str:
        return f"EagerPhenopacketInfo(path={self._path})"

    def __repr__(self) -> str:
        return str(self)


class ZipPhenopacketInfo(PhenopacketInfo):
    """
    Represents phenopacket information stored in a zip file.

    Attributes:
        path (str): The file path to the zip file containing the phenopacket.
        pp_path (zipfile.Path): The path to the phenopacket within the zip file.
    """

    def __init__(self, path: str, pp_path: zipfile.Path):
        self._path = path
        self._pp_path = pp_path

    @property
    def path(self) -> str:
        return self._path

    @property
    def phenopacket(self) -> Phenopacket:
        return Parse(self._pp_path.read_text(), Phenopacket())

    def __str__(self) -> str:
        return f"ZipPhenopacketInfo(path={self._pp_path})"

    def __repr__(self) -> str:
        return f"ZipPhenopacketInfo(path={self._pp_path})"