from ppktstore.validation import UniquePhenopacketId, PhenopacketStoreAuditor
from ppktstore.model import CohortInfo, DefaultPhenopacketStore, EagerPhenopacketInfo
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket


def make_phenopacket(id: str):
    pp = Phenopacket()
    pp.id = id
    return pp


def make_cohort(name: str, ids):
    infos = [EagerPhenopacketInfo.from_phenopacket(str(i), make_phenopacket(i)) for i in ids]
    return CohortInfo(name, name, infos)


def make_store(cohorts):
    return DefaultPhenopacketStore("teststore", None, cohorts)


class TestUniquePhenopacketId:

    def test_unique_phenopacket_id_error(self):
        # Two cohorts, overlapping phenopacket id 'A'
        cohort1 = make_cohort('cohort1', ['A', 'B'])
        cohort2 = make_cohort('cohort2', ['A', 'C'])
        store = make_store([cohort1, cohort2])
        auditor = UniquePhenopacketId()
        notepad = PhenopacketStoreAuditor.prepare_notepad("test-ps")
        auditor.audit(store, notepad)
        assert notepad.has_errors_or_warnings(include_subsections=False)

    def test_unique_phenopacket_id_pass(self):
        # Two cohorts, all ids unique
        cohort1 = make_cohort('cohort1', ['A', 'B'])
        cohort2 = make_cohort('cohort2', ['C', 'D'])
        store = make_store([cohort1, cohort2])
        auditor = UniquePhenopacketId()
        notepad = PhenopacketStoreAuditor.prepare_notepad("test-ps")
        auditor.audit(store, notepad)
        assert not notepad.has_errors_or_warnings(include_subsections=False)
