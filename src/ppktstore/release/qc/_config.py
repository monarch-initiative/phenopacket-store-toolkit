from ._api import PhenopacketStoreAuditor
from ._checks import DefaultPhenopacketStoreAuditor, UniqueIdsCheck, NoUnwantedCharactersCheck


def configure_qc_checker() -> PhenopacketStoreAuditor:
    checks = (
        UniqueIdsCheck(),
        NoUnwantedCharactersCheck.no_whitespace(),
    )
    return DefaultPhenopacketStoreAuditor(checks=checks)
