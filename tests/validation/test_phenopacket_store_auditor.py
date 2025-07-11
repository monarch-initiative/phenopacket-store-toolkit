import pytest

from ppktstore.model import PhenopacketStore
from ppktstore.validation import PhenopacketStoreAuditor, default_auditor
import zipfile
import os


class TestPhenopacketAuditor:

    @pytest.fixture(scope="class")
    def auditor(self) -> PhenopacketStoreAuditor:
        return default_auditor()

    @pytest.fixture(scope="class")
    def phenopacket_store(self,
        fpath_ps_release_zip: str,
    ):
        with zipfile.ZipFile(fpath_ps_release_zip) as zip_file:
            yield PhenopacketStore.from_release_zip(
                zip_file=zip_file,
            )

    @pytest.fixture(scope="class")
    def phenopacket_store_fail_single_cohort(self, fpath_test_data: str):
        p = os.path.join(fpath_test_data, "test_get_store_zip1.zip")
        with zipfile.ZipFile(p) as zip_file:
            yield PhenopacketStore.from_release_zip(
                zip_file=zip_file,
            )

    @pytest.fixture(scope="class")
    def phenopacket_store_fail_multi_cohort(self, fpath_test_data: str):
        p = os.path.join(fpath_test_data, "test_get_store_zip2.zip")
        with zipfile.ZipFile(p) as zip_file:
            yield PhenopacketStore.from_release_zip(
                zip_file=zip_file,
            )

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