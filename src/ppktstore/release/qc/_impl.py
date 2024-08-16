import logging

from ._config import configure_qc_checker

from ppktstore.model import PhenopacketStore


def qc_phenopackets(
    store: PhenopacketStore,
    logger: logging.Logger,
) -> int:
    logger.info('Checking phenopackets')
    checker = configure_qc_checker()
    results = checker.check(phenopacket_store=store)
    if results.is_ok():
        logger.info('No Q/C issues were found')
        return 0
    else:
        logger.info('Phenopacket store Q/C failed')
        
        for checker_name, issues in results.iter_results():
            logger.info('\'%s\' found %d error(s):', checker_name, len(issues))
            for error in issues:
                logger.info(' - %s', error)
        return 1
