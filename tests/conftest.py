import os
import zipfile

import pytest

from ppktstore.model import PhenopacketStore


@pytest.fixture(scope="session")
def fpath_test_data() -> str:
    fpath_test_dir = os.path.join(os.getcwd(), "tests")
    return os.path.join(fpath_test_dir, "test_data")


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


@pytest.fixture(scope="session")
def phenopacket_store(
    fpath_ps_release_zip: str,
):
    with zipfile.ZipFile(fpath_ps_release_zip) as zip_file:
        yield PhenopacketStore.from_release_zip(
            zip_file=zip_file,
        )
