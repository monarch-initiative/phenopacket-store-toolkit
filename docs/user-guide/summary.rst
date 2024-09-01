.. _summary:

=========================
Phenopacket Store Summary
=========================

phenopacket-store-toolkit provides functions to generate various summaries and visualizations of the phenopackets and 
cohorts contained in a release. We use these functions to generate a summary of each 
`Phenopacket-Store release <https://github.com/monarch-initiative/phenopacket-store/blob/main/PhenopacketStoreStats.ipynb>`_.

Interested users should study the notebook file to learn how to access the functions.

Display cohorts sorted by size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the functions shown in the notebook, the following function will generate a Pandas
table with all cohorts sorted according to size. ::

    from ppktstore.model import PhenopacketStore
    from ppktstore.release.stats import PPKtStoreStats
    import zipfile
    ppkt_zip_path = "../your/path/all_phenopackets.zip'
    with zipfile.ZipFile(ppkt_zip_path) as zf:
        store = PhenopacketStore.from_release_zip(zf)
    stats = PPKtStoreStats(store)
    df = stats.get_disease_count_table()
    df.head()
    # ...


