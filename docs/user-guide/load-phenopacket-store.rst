.. _load-phenopacket-store:

======================
Load Phenopacket Store
======================

Phenopacket Store Toolkit simplifies loading the Phenopacket Store cohorts.
The toolkit removes the boilerplate required for downloading and keeping track of the release files, 
and for phenopacket I/O.


Load a single phenopacket cohort
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here we show how to load phenopackets of a *SUOX* cohort from Phenopacket Store release `0.1.18`.

We start with the imports:

>>> from ppktstore.registry import configure_phenopacket_registry
>>> registry = configure_phenopacket_registry()

We created a :class:`ppktstore.registry.PhenopacketStoreRegistry` to manage the release files.
By default, the registry stores the release ZIP files at ``$HOME/.phenopacket-store`` for Unix, 
or ``$HOME/phenopacket-store`` for Windows. 

Now let's load the phenopackets.

>>> with registry.open_phenopacket_store(release="0.1.18") as ps:
...     phenopackets = list(ps.iter_cohort_phenopackets("SUOX"))
>>> len(phenopackets)
35

We open Phenopacket Store with release `0.1.18`. Behind the scenes, the registry checks if the ZIP file
has been previously downloaded. If absent, the ZIP file is fetched from GitHub. 
This is followed by opening the ZIP file and creating :class:`ppktstore.model.PhenopacketStore` (``ps``).
We can load phenopackets for a cohort name (e.g. *SUOX*). The phenopackets are loaded lazily, 
and we collect them into a list. 

We loaded 35 phenopackets!
