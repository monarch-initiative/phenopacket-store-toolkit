from ._api import QcChecker
from ._checks import DefaultQcChecker, UniqueIdsCheck


def configure_qc_checker() -> QcChecker:
    checks = (UniqueIdsCheck(),)
    return DefaultQcChecker(checks=checks)
