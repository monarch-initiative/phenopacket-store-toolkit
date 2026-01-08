import abc
import dataclasses
import os
import pathlib
import re
import typing
import zipfile

from collections import defaultdict

from google.protobuf.json_format import Parse
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket, Cohort

from ._zip_util import relative_to

_FILEFORMAT_SUFFIXES = re.compile(r"\.(json|pb)$")


class PhenopacketInfo(metaclass=abc.ABCMeta):
    """
    Phenopacket info includes a phenopacket plus metadata,
    which at this time is just a relative path wrt. the enclosing cohort.
    """

    @property
    @abc.abstractmethod
    def path(self) -> str:
        """
        Path of the phenopacket source relative from the enclosing cohort.
        """

    @property
    @abc.abstractmethod
    def phenopacket(self) -> Phenopacket:
        """
        The phenopacket.
        """
        pass


class EagerPhenopacketInfo(PhenopacketInfo):
    """
    Phenopacket info with eagerly loaded phenopacket.
    """

    @staticmethod
    def from_path(
        path: str,
        pp_path: pathlib.Path,
    ) -> "EagerPhenopacketInfo":
        """
        Load phenopacket from a `pp_path`.
        """
        pp = Parse(pp_path.read_text(), Phenopacket())
        return EagerPhenopacketInfo.from_phenopacket(path, pp)

    @staticmethod
    def from_phenopacket(
        path: str,
        pp: Phenopacket,
    ) -> "EagerPhenopacketInfo":
        """
        Create `EagerPhenopacketInfo` from a provided phenopacket.
        """
        return EagerPhenopacketInfo(path, pp)

    def __init__(
        self,
        path: str,
        phenopacket: Phenopacket,
    ):
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


@dataclasses.dataclass
class CohortInfo:
    """
    Cohort of a Phenopacket store.

    Includes cohort-level metadata and a sequence of phenopacket infos for the included phenopackets.
    """

    name: str
    """
    Cohort name, e.g. `FBN1`.
    """

    path: str
    """
    Path of the cohort relative from the enclosing source.
    """

    phenopackets: typing.Sequence[PhenopacketInfo]
    """
    A sequence of cohort's phenopacket infos.
    """

    def iter_phenopackets(self) -> typing.Iterator[Phenopacket]:
        """
        Get an iterator with all phenopackets belonging to the cohort.
        """
        return map(lambda pi: pi.phenopacket, self.phenopackets)

    @property
    def cohort(self) -> Cohort:
        """
        Create a Phenopacket Schema :class:`Cohort` from the cohort info.

        The :meth:`CohortInfo.name` is used as `cohort.id`
        and the phenopackets are added into `cohort.members`.

        No cohort-level meta data is created.
        """
        return Cohort(
            id=self.name,
            members=(pi.phenopacket for pi in self.phenopackets),
        )

    def export_phenopackets_to_directory(
        self,
        path: typing.Union[pathlib.Path, str],
        format: typing.Literal["pb", "json"] = "json",
    ):
        """
        Export the phenopackets into a directory.

        Each phenopacket is exported into a single file.
        The directory is created if it does not exist.

        :param path: path to the output directory.
        :param format: phenopacket file format, one of ``{"pb", "json"}`` for Protobuf and JSON format, respectively.
        :raises ValueError: if `output` does not point to a directory.
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        if not os.path.isdir(path):
            raise ValueError(f"output {path} does is not a directory")

        match format:
            case "json":
                from google.protobuf.json_format import MessageToJson

                for pi in self.phenopackets:
                    fpath_out = os.path.join(path, f"{pi.path}.json")
                    with open(fpath_out, "w") as fh:
                        fh.write(MessageToJson(pi.phenopacket))
            case "pb":
                for pi in self.phenopackets:
                    fpath_out = os.path.join(path, f"{pi.path}.pb")
                    with open(fpath_out, "wb") as fh:
                        fh.write(pi.phenopacket.SerializeToString())
            case _:
                raise ValueError(f"Invalid format {format}")

    def __len__(self) -> int:
        return len(self.phenopackets)


class PhenopacketStore(metaclass=abc.ABCMeta):
    """
    `PhenopacketStore` provides the data and metadata for Phenopacket Store cohorts.

    Use :func:`from_release_zip` or :func:`from_notebook_dir` to open a store instance.
    """

    @staticmethod
    def from_release_zip(
        zip_file: zipfile.ZipFile,
        strategy: typing.Literal["eager", "lazy"] = "eager",
    ) -> "PhenopacketStore":
        """
        Read `PhenopacketStore` from a release ZIP archive.

        The archive structure must match the structure of the ZIP archives
        created by :class:`ppktstore.archive.PhenopacketStoreArchiver`.
        Only JSON phenopacket format is supported at the moment.

        Strategy
        ^^^^^^^^

        The phenopackets can be loaded in an *eager* or *lazy* fashion.

        The `'eager'` strategy loads *all* phenopackets during the execution
        of this function. This may do more work than necessary,
        especially if only several cohorts are needed.

        The `'lazy'` strategy only scans the ZIP for phenopackets
        and the actual parsing is done on demand, when accessing
        the :attr:`PhenopacketInfo.phenopacket` property.
        In result, the lazy loading will only succeed if the ZIP handle is kept open.

        .. note::

          We recommend using Python's context manager to ensure `zip_handle` is closed:

          >>> import zipfile
          >>> with zipfile.ZipFile("all_phenopackets.zip") as zf:  # doctest: +SKIP
          ...   ps = PhenopacketStore.from_release_zip(zf)
          ...   # Do things here...

        :param zip_file: a ZIP archive handle.
        :param strategy: a `str` with strategy for loading phenopackets, one of `{'eager', 'lazy'}`.
        :returns: :class:`PhenopacketStore` with data read from the archive.
        """
        assert strategy in (
            "eager",
            "lazy",
        ), f"Strategy must be either `eager` or `lazy`: {strategy}"

        root = zipfile.Path(zip_file)

        # Prepare paths to cohort folders
        # and collate paths to cohort phenopackets.
        cohort2path = {}
        cohort2pp_paths = defaultdict(list)
        for entry in zip_file.infolist():
            entry_path = zipfile.Path(zip_file, at=entry.filename)
            if entry_path.is_dir():
                entry_parent = relative_to(root, entry_path.parent)
                if entry_parent in ("", "."):
                    name = entry_path.name
                else:
                    cohort_name = entry_path.name
                    cohort2path[cohort_name] = entry_path
            elif entry_path.is_file() and entry_path.name.endswith(".json"):
                # This SHOULD be a phenopacket!
                cohort = entry_path.parent.name  # type: ignore
                cohort2pp_paths[cohort].append(entry_path)

        # Put cohorts together
        cohorts = []
        for cohort, cohort_path in cohort2path.items():
            if cohort in cohort2pp_paths:
                at = relative_to(cohort_path, root)
                rel_cohort_path = zipfile.Path(
                    zip_file,
                    at=at,
                )
                pp_infos = []
                for pp_path in cohort2pp_paths[cohort]:
                    path = relative_to(pp_path, cohort_path)
                    path = re.sub(_FILEFORMAT_SUFFIXES, "", path)
                    if strategy == "eager":
                        pi = EagerPhenopacketInfo.from_path(path, pp_path)
                    elif strategy == "lazy":
                        pi = ZipPhenopacketInfo(
                            path=path,
                            pp_path=pp_path,
                        )
                    pp_infos.append(pi)

                ci = CohortInfo(
                    name=cohort,
                    path=str(rel_cohort_path),
                    phenopackets=tuple(pp_infos),
                )
                cohorts.append(ci)

        path = pathlib.Path(str(root))

        return PhenopacketStore.from_cohorts(
            name=name,
            path=path,
            cohorts=cohorts,
        )

    @staticmethod
    def from_notebook_dir(
        nb_dir: str,
        pp_dir: str = "phenopackets",
    ) -> "PhenopacketStore":
        """
        Create `PhenopacketStore` from Phenopacket store notebook dir `nb_dir`.

        We expect the `nb_dir` to include a folder per cohort,
        and the phenopackets should be stored in `pp_dir` sub-folder (``pp_dir="phenopackets"`` by default).

        The phenopackets are loaded *eagerly* into memory.

        .. note::

          The function is intended for private use only and we encourage
          using the Phenopacket Store registry API presented in :ref:`load-phenopacket-store` section.
        """
        cohorts = []
        nb_path = pathlib.Path(nb_dir)
        for cohort_name in os.listdir(nb_path):
            cohort_dir = nb_path.joinpath(cohort_name)
            if cohort_dir.is_dir():
                cohort_path = cohort_dir.joinpath(pp_dir)
                if cohort_path.is_dir():
                    pp_infos = []
                    rel_cohort_path = cohort_path.relative_to(nb_path)
                    for filename in os.listdir(cohort_path):
                        if filename.endswith(".json"):
                            filepath = cohort_path.joinpath(filename)
                            path = re.sub(_FILEFORMAT_SUFFIXES, "", filename)
                            pp = Parse(filepath.read_text(), Phenopacket())
                            pi = EagerPhenopacketInfo(
                                path=path,
                                phenopacket=pp,
                            )
                            pp_infos.append(pi)

                    cohorts.append(
                        CohortInfo(
                            name=cohort_name,
                            path=str(rel_cohort_path),
                            phenopackets=tuple(pp_infos),
                        )
                    )

        return PhenopacketStore.from_cohorts(
            name=nb_path.name,
            path=nb_path,
            cohorts=cohorts,
        )

    @staticmethod
    def from_cohorts(
        name: str,
        path: pathlib.Path,
        cohorts: typing.Iterable[CohortInfo],
    ) -> "PhenopacketStore":
        """
        Create `PhenopacketStore` from cohorts.

        :param name: a `str` with the store name (e.g. `v0.1.23` or any other `str` will do).
        :param path: a path to the store root to resolve phenopacket locations.
        :param cohorts: an iterable with cohorts.
        """
        return DefaultPhenopacketStore(
            name=name,
            path=path,
            cohorts=cohorts,
        )

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Get a `str` with the Phenopacket Store name. Most of the time,
        the name corresponds to the release tag (e.g. `0.1.18`).
        """
        pass

    @property
    @abc.abstractmethod
    def path(self) -> pathlib.Path:
        """
        Get path to the phenopacket store resource.
        """
        pass

    @abc.abstractmethod
    def cohorts(self) -> typing.Collection[CohortInfo]:
        """
        Get a collection of all Phenopacket Store cohorts.
        """
        pass

    @abc.abstractmethod
    def cohort_for_name(
        self,
        name: str,
    ) -> CohortInfo:
        """
        Retrieve a Phenopacket Store cohort by its name.

        :param name: a `str` with the cohort name (e.g. ``SUOX``).
        :raises KeyError: if no cohort with such name exists.
        """
        pass

    def iter_cohort_phenopackets(
        self,
        name: str,
    ) -> typing.Iterator[Phenopacket]:
        """
        Get an iterator with all phenopackets of a cohort.

        :param name: a `str` with the cohort name.
        """
        return self.cohort_for_name(name).iter_phenopackets()

    def cohort_names(self) -> typing.Iterator[str]:
        """
        Get an iterator with names of all Phenopacket Store cohorts.
        """
        return map(lambda ci: ci.name, self.cohorts())

    def cohort_count(self) -> int:
        """
        Compute the count of Phenopacket Store cohorts.
        """
        return len(self.cohorts())

    def phenopacket_count(self) -> int:
        """
        Compute the total number of phenopackets available in Phenopacket Store.
        """
        return sum(len(cohort) for cohort in self.cohorts())


class DefaultPhenopacketStore(PhenopacketStore):
    def __init__(
        self,
        name: str,
        path: pathlib.Path,
        cohorts: typing.Iterable[CohortInfo],
    ):
        self._name = name
        self._path = path
        self._cohorts = {cohort.name: cohort for cohort in cohorts}

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> pathlib.Path:
        return self._path

    def cohorts(self) -> typing.Collection[CohortInfo]:
        return self._cohorts.values()

    def cohort_for_name(
        self,
        name: str,
    ) -> CohortInfo:
        return self._cohorts[name]


class ZipPhenopacketInfo(PhenopacketInfo):
    """
    Loads phenopacket from a Zip file on demand.
    """

    # NOT PART OF THE PUBLIC API

    def __init__(
        self,
        path: str,
        pp_path: zipfile.Path,
    ):
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
        return f"ZipPhenopacketInfo(path={self._path}, pp_path={self._pp_path})"
