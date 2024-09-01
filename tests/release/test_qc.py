import zipfile

import pytest
from ppktstore.model import PhenopacketStore
from ppktstore.release.qc import configure_qc_checker, PhenopacketStoreAuditor


class TestPhenopacketStoreAuditor:

    @pytest.fixture(scope="class")
    def auditor(self) -> PhenopacketStoreAuditor:
        return configure_qc_checker()

    @pytest.fixture(scope="class")
    def phenopacket_store(
        self,
        fpath_ps_release_zip: str,
    ) -> PhenopacketStore:
        with zipfile.ZipFile(fpath_ps_release_zip) as zfh:
            return PhenopacketStore.from_release_zip(zip_file=zfh, strategy="eager")

    def test_audit(
        self,
        auditor: PhenopacketStoreAuditor,
        phenopacket_store: PhenopacketStore,
    ):
        notepad = PhenopacketStoreAuditor.prepare_notepad("test-ps")
        auditor.audit(
            item=phenopacket_store,
            notepad=notepad,
        )

        assert not notepad.has_errors_or_warnings(include_subsections=False)
