import logging
import typing

from ppktstore.model import PhenopacketStore

from ._archiver import PhenopacketStoreArchiver, ArchiveFormat


def package_phenopackets(
    store: PhenopacketStore,
    formats: typing.Iterable[str],
    filename: str,
    top_level_folder: str,
    logger: logging.Logger,
) -> int:
    logger.info("Using archive base name `%s`", filename)
    logger.info("Putting cohorts to top-level directory `%s`", top_level_folder)
    logger.info("Using %s archive format(s) ", ", ".join(formats))

    archiver = PhenopacketStoreArchiver()

    afs = [ArchiveFormat[fmt.upper()] for fmt in formats]
    for format in afs:
        logger.info("Preparing %s archive", format.name)
        archiver.prepare_archive(
            store=store,
            format=format,
            filename=filename,
            top_level_folder=top_level_folder,
            flat=False,
        )

    logger.info("Done!")
    return 0
