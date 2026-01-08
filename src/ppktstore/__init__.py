"""
Phenopacket Store Toolkit helps with Phenopacket Store release and Q/C
and simplifies access to the store data for the downstream applications.
"""

from importlib.metadata import version

from . import registry
from . import model

# We do not import `.release` package since it requires extra dependencies.

__version__ = version("phenopacket-store-toolkit")

__all__ = [
    "registry",
    "model",
]
