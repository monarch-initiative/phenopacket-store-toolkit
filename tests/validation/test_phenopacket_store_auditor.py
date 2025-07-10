import pytest

from ppktstore.model import PhenopacketStore
from ppktstore.validation import PhenopacketStoreAuditor, default_auditor


class TestPhenopacketAuditor:

    @pytest.fixture(scope="class")
    def auditor(self) -> PhenopacketStoreAuditor:
        return default_auditor()

    def test_phenopacket_store_cohort_fail(
        self,
        auditor: PhenopacketStoreAuditor,
        phenopacket_store_fail_single_cohort: PhenopacketStore):
        """
            Test that a cohort within a phenopacket store throws an error with duplicate phenopacket IDs
            fails validation.
        """
        notepad = PhenopacketStoreAuditor.prepare_notepad("test-ps")
        # Create a bad cohort that has 2 phenopackets with the same id
        auditor.audit(
            item=phenopacket_store_fail_single_cohort,
            notepad=notepad
        )
        assert not notepad.has_errors_or_warnings(include_subsections=False)
        for section in notepad.iter_sections():
            if section.has_errors_or_warnings(include_subsections=False):
                assert (list(section.errors())[0].message ==
                        "`PMID_28239884_Family_1_proband` is not unique in cohort `BADX`")

    def test_phenopacket_store_cohort_fail_multi(
        self,
        auditor: PhenopacketStoreAuditor,
        phenopacket_store_fail_multi_cohort: PhenopacketStore):
        """
            Test that a cohort within a phenopacket store throws an error with duplicate phenopacket IDs
            fails validation.
        """
        notepad = PhenopacketStoreAuditor.prepare_notepad("test-ps")
        # Create a bad cohort that has 2 phenopackets with the same id
        auditor.audit(
            item=phenopacket_store_fail_multi_cohort,
            notepad=notepad,
        )
        for section in notepad.iter_sections():
            if section.level > 0:
                assert not section.has_errors_or_warnings(include_subsections=False)
            else:
                assert section.has_errors_or_warnings(include_subsections=False)