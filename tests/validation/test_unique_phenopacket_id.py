import pathlib
import typing

import pytest

from ppktstore.validation import UniquePhenopacketId
from ppktstore.model import CohortInfo, PhenopacketStore, EagerPhenopacketInfo
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket


def make_phenopacket(
    id: str,
) -> Phenopacket:
    pp = Phenopacket()
    pp.id = id
    return pp


def make_cohort(
    name: str,
    ids: typing.Iterable[str],
) -> CohortInfo:
    infos = [
        EagerPhenopacketInfo.from_phenopacket(str(i), make_phenopacket(i)) for i in ids
    ]
    return CohortInfo(name, name, infos)


def make_store(cohorts) -> PhenopacketStore:
    return PhenopacketStore.from_cohorts("teststore", pathlib.Path("."), cohorts)


class TestUniquePhenopacketId:
    @pytest.fixture
    def check(self) -> UniquePhenopacketId:
        return UniquePhenopacketId()

    def test_unique_phenopacket_id_error(
        self,
        check: UniquePhenopacketId,
    ):
        # Two cohorts, overlapping phenopacket id 'A'
        cohort1 = make_cohort("cohort1", ["A", "B"])
        cohort2 = make_cohort("cohort2", ["A", "C"])
        store = make_store([cohort1, cohort2])

        notepad = check.prepare_notepad("test-ps")
        check.audit(store, notepad)

        assert notepad.has_errors_or_warnings(include_subsections=False)

        errors = tuple(notepad.errors())
        assert len(errors) == 1
        error = errors[0]
        assert error.message == "`A` is present in 2 cohorts: ['cohort1', 'cohort2']"
        assert error.solution is None

    def test_unique_phenopacket_id_pass(
        self,
        check: UniquePhenopacketId,
    ):
        # Two cohorts, all ids unique
        cohort1 = make_cohort("cohort1", ["A", "B"])
        cohort2 = make_cohort("cohort2", ["C", "D"])
        store = make_store([cohort1, cohort2])

        notepad = check.prepare_notepad("test-ps")
        check.audit(store, notepad)

        assert not notepad.has_errors_or_warnings(include_subsections=False)
