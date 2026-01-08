import zipfile

import pytest

from ppktstore.model import CohortInfo, PhenopacketStore


@pytest.fixture(scope="module")
def phenopacket_store(
    fpath_ps_release_zip: str,
) -> PhenopacketStore:
    with zipfile.ZipFile(fpath_ps_release_zip) as zip_file:
        return PhenopacketStore.from_release_zip(
            zip_file=zip_file,
            strategy="eager",
        )


class TestCohortInfo:
    @pytest.fixture(scope="class")
    def cohort_info(
        self,
        phenopacket_store: PhenopacketStore,
    ) -> CohortInfo:
        return phenopacket_store.cohort_for_name("AAGAB")

    def test_cohort(
        self,
        cohort_info: CohortInfo,
    ):
        cohort = cohort_info.cohort

        assert cohort.id == "AAGAB"

        assert len(cohort.members) == 3
        assert list(pp.id for pp in cohort.members) == [
            "PMID_28239884_Family_1_proband",
            "PMID_28239884_Family_2_proband",
            "PMID_28239884_Family_3_proband",
        ]
