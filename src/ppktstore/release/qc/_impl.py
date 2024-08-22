import io
import logging

from ._config import configure_qc_checker

from ppktstore.model import PhenopacketStore


def qc_phenopackets(
    store: PhenopacketStore,
    logger: logging.Logger,
) -> int:
    logger.info('Checking phenopackets')
    auditor = configure_qc_checker()
    notepad = auditor.prepare_notepad(store.name)
    auditor.audit(
        item=store,
        notepad=notepad,
    )

    buf = io.StringIO()
    notepad.summarize(file=buf)
    if notepad.has_errors_or_warnings(include_subsections=True):
        logger.error(buf.getvalue())
        return 1
    else:
        logger.info(buf.getvalue())
        return 0
