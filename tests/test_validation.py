import zipfile
import hpotk
import pytest

from ppktstore.model import PhenopacketStore
from ppktstore.validation import PhenopacketStoreAuditor


class TestPhenopacketStoreAuditor:
    @pytest.fixture(scope="class")
    def phenopacket_store(
        self,
        fpath_ps_release_zip: str,
    ):
        with zipfile.ZipFile(fpath_ps_release_zip) as zip_file:
            yield PhenopacketStore.from_release_zip(
                zip_file=zip_file,
            )

    @pytest.fixture(scope="class")
    def auditor(
        self,
        hpo: hpotk.MinimalOntology,
    ) -> PhenopacketStoreAuditor:
        return PhenopacketStoreAuditor.default_auditor(hpo)

    def test_audit(
        self,
        auditor: PhenopacketStoreAuditor,
        phenopacket_store: PhenopacketStore,
    ):
        notepad = auditor.prepare_notepad(phenopacket_store.name)

        auditor.audit(phenopacket_store, notepad)

        assert notepad.summary() == "No errors or warnings were found\n"
