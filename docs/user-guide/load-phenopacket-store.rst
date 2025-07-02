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


Export a phenopacket cohort
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Phenopackets of a cohort can easily be exported into a directory for further processing.
The export is implemented on the :class:`~ppktstore.model.CohortInfo` class of the Phenopacket Store API:

>>> outdir = "dev/SUOX"
>>> with registry.open_phenopacket_store(release="0.1.18") as ps:
...     cohort = ps.cohort_for_name("SUOX")
...     cohort.export_phenopackets_to_directory(outdir)

We open Phenopacket Store and get the :class:`~ppktstore.model.CohortInfo` for the *SUOX* cohort.
Then we export the phenopackets into a directory (e.g. ``"dev/SUOX"``)

We can check if the phenopackets were exported:

>>> import os
>>> paths = sorted(os.listdir(outdir))
>>> paths[:5]  # doctest: +NORMALIZE_WHITESPACE
['PMID_36303223_individual_10_PMID_12112661.json',
 'PMID_36303223_individual_11_PMID_12112661.json',
 'PMID_36303223_individual_12_PMID_12112661.json',
 'PMID_36303223_individual_13_PMID_12112661.json',
 'PMID_36303223_individual_14_PMID_11825068.json']

.. Clean up the folder
.. doctest::
  :hide:

  >>> for fp in os.listdir(outdir): os.remove(os.path.join(outdir, fp))
  >>> os.rmdir(outdir)

By default, the phenopackets are stored in JSON format. However, Protobuf wire format is also supported:

>>> with registry.open_phenopacket_store(release="0.1.18") as ps:
...     cohort = ps.cohort_for_name("SUOX")
...     cohort.export_phenopackets_to_directory(outdir, format="pb")
>>> sorted(os.listdir(outdir))[:5] # doctest: +NORMALIZE_WHITESPACE
['PMID_36303223_individual_10_PMID_12112661.pb',
 'PMID_36303223_individual_11_PMID_12112661.pb',
 'PMID_36303223_individual_12_PMID_12112661.pb',
 'PMID_36303223_individual_13_PMID_12112661.pb',
 'PMID_36303223_individual_14_PMID_11825068.pb']

We use the ``format`` option to export phenopackets as Protobuf files.


.. Clean up the folder
.. doctest::
  :hide:

  >>> for fp in os.listdir(outdir): os.remove(os.path.join(outdir, fp))
  >>> os.rmdir(outdir)
