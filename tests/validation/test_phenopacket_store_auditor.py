import logging, pytest
from pathlib import Path

from ppktstore.model import PhenopacketStore, CohortInfo, EagerPhenopacketInfo
from ppktstore.validation import PhenopacketStoreAuditor, default_auditor


class TestPhenopacketAuditor:

    @pytest.fixture(scope="class")
    def auditor(self) -> PhenopacketStoreAuditor:
        return default_auditor()

    def test_phenopacket_store_cohort_fail(
        self,
        auditor: PhenopacketStoreAuditor,
        phenopacket_store: PhenopacketStore,
        fpath_test_data: str
    ):
        """
            Test that a cohort within a phenopacket store throws an error with duplicate phenopacket IDs
            fails validation.
        """
        notepad = PhenopacketStoreAuditor.prepare_notepad("test-ps")
        # Create a bad cohort that has 2 phenopackets with the same id
        pspath = "{0}/{1}".format(fpath_test_data, "test_get_store_zip1/")
        cohortpath = "{0}{1}".format(pspath, "BADX")
        ps = PhenopacketStore.from_cohorts(
            name = "bad_store",
            path= Path(pspath),
            cohorts=[
                CohortInfo("BADX", cohortpath,
                           phenopackets=[
                               EagerPhenopacketInfo.from_path(
                                   "{0}/{1}".format(cohortpath, "PMID_28239884_Family1proband.json"),
                                   Path("{0}/{1}".format(cohortpath, "PMID_28239884_Family1proband.json"))),
                               EagerPhenopacketInfo.from_path(
                                   "{0}/{1}".format(cohortpath, "PMID_28239884_Family2proband.json"),
                                   Path("{0}/{1}".format(cohortpath, "PMID_28239884_Family2proband.json")))

                           ])
            ])
        auditor.audit(
            item=ps,
            notepad=notepad,
        )
        assert not notepad.has_errors_or_warnings(include_subsections=False)
        assert notepad.has_errors_or_warnings(include_subsections=True)
        for section in notepad.iter_sections():
            if section.has_errors_or_warnings(include_subsections=False):
                   assert (list(section.errors())[0].message ==
                           "`PMID_28239884_Family_1_proband` is not unique in cohort `BADX`")