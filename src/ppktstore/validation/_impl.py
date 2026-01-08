import io
import logging

import hpotk

from ..model import PhenopacketStore
from ._ps_auditor import PhenopacketStoreAuditor


def qc_phenopacket_store(
    store: PhenopacketStore,
    hpo: hpotk.MinimalOntology,
    logger: logging.Logger,
) -> int:
    logger.info("Checking phenopacket store")
    auditor = PhenopacketStoreAuditor.default_auditor(hpo)
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
