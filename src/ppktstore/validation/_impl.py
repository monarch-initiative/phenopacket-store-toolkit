from ..model import PhenopacketStore
from ._auditor import default_auditor
import logging
import io

def qc_phenopacket_store(
    store: PhenopacketStore,
    logger: logging.Logger
) -> int:
    logger.info('Checking phenopacket store')
    auditor = default_auditor()
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