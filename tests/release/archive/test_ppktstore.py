import os
import tarfile
import typing
import zipfile
from pathlib import Path

import pytest

from ppktstore.model import PhenopacketStore
from ppktstore.release.archive import PhenopacketStoreArchiver, ArchiveFormat


class TestPPKtStore:

    @pytest.fixture(scope="class")
    def phenopacket_store(
        self,
        fpath_nb_dir: str,
    ) -> PhenopacketStore:
        return PhenopacketStore.from_notebook_dir(fpath_nb_dir)

    def test_get_store_zip(
        self,
        phenopacket_store: PhenopacketStore,
        tmp_path: Path,
    ):
        filename = str(tmp_path)
        basename = os.path.basename(tmp_path)

        archiver = PhenopacketStoreArchiver()
        archiver.prepare_archive(
            store=phenopacket_store,
            format=ArchiveFormat.ZIP,
            filename=filename,
            top_level_folder=basename,
        )

        expected_archive_filename = f"{filename}.zip"
        assert os.path.isfile(expected_archive_filename)

        basename = os.path.basename(tmp_path)

        with zipfile.ZipFile(expected_archive_filename) as zf:
            filenames = tuple(file.filename for file in zf.filelist)

        TestPPKtStore.check_archive_spec(basename, filenames)

    def test_get_store_gzip(
        self,
        phenopacket_store: PhenopacketStore,
        tmp_path: Path,
    ):
        filename = str(tmp_path)
        basename = os.path.basename(tmp_path)

        archiver = PhenopacketStoreArchiver()
        archiver.prepare_archive(
            store=phenopacket_store,
            format=ArchiveFormat.TGZ,
            filename=filename,
            top_level_folder=basename,
        )

        expected_archive_filename = f"{filename}.tgz"
        assert os.path.isfile(expected_archive_filename)

        with tarfile.open(expected_archive_filename) as fh:
            names = fh.getnames()
            filenames = tuple(name for name in names if name != "")

        TestPPKtStore.check_archive_spec(basename, filenames)

    @pytest.mark.parametrize(
        "suffix",
        [
            ".gz",
            ".tgz",
            ".tar.gz",
            ".zip",
            ".jar",
        ],
    )
    def test_suffix_in_outfilename_explodes(
        self,
        phenopacket_store: PhenopacketStore,
        suffix: str,
    ):
        filename = f"whatever{suffix}"
        archiver = PhenopacketStoreArchiver()
        with pytest.raises(ValueError) as ctx:
            archiver.prepare_archive(
                phenopacket_store,
                format=ArchiveFormat.ZIP,
                filename=filename,
            )

        assert (
            ctx.value.args[0]
            == f"The path must not include suffix but found {suffix} in {filename}"
        )

    @staticmethod
    def check_archive_spec(
        basename: str,
        filenames: typing.Iterable[str],
    ):
        assert any(
            file == f"{basename}/phenopacket_store.summary.tsv" for file in filenames
        ), "The archive should include the summary TSV file"

        json_files = tuple(file for file in filenames if file.endswith(".json"))
        assert len(json_files) == 10, "The archive should include 10 JSON phenopackets"

        n_top_level = 0
        for file_name in filenames:
            n_seps = sum(1 for char in file_name if char == os.sep)
            if n_seps == 0 or (n_seps == 1 and file_name.endswith(os.sep)):
                n_top_level += 1
        assert n_top_level == 1, "The archive should include only one top-level element"

        assert all(
            file.startswith(basename) for file in filenames
        ), "All files should be located in the top-level directory"
