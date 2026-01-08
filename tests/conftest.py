import os
import pytest

import hpotk


@pytest.fixture(scope="session")
def fpath_test_data() -> str:
    fpath_test_dir = os.path.join(os.getcwd(), "tests")
    return os.path.join(fpath_test_dir, "test_data")


@pytest.fixture(scope="session")
def fpath_hpo(
    fpath_test_data: str,
) -> str:
    return os.path.join(fpath_test_data, "hp.v2024-04-26.json.gz")


@pytest.fixture(scope="session")
def hpo(
    fpath_hpo: str,
) -> hpotk.MinimalOntology:
    return hpotk.load_minimal_ontology(fpath_hpo)


@pytest.fixture(scope="session")
def fpath_nb_dir(
    fpath_test_data: str,
) -> str:
    return os.path.join(fpath_test_data, "notebooks")


@pytest.fixture(scope="session")
def fpath_ps_release_zip(
    fpath_test_data: str,
) -> str:
    return os.path.join(fpath_test_data, "test_get_store_zip0.zip")
