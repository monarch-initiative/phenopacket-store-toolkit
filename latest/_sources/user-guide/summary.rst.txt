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

Note that some of the cohorts (which are usually gene-based) contain multiple disease entities. 
To get the total counts per cohort, the following code can be used. ::

    df_grouped = df.groupby('cohort')['count'].sum().reset_index()
    df_sorted = df_grouped.sort_values(by='count', ascending=False)
    df_sorted = df_sorted[["cohort", "count"]]
    df_sorted.reset_index(drop=True, inplace=True)

This will produce a table something like the following.

+-----------+-------+
| cohort    | count |
+===========+=======+
| STXBP1    | 463   |
+-----------+-------+
| SCN2A     | 393   |
+-----------+-------+
| ANKRD11   | 337   |
+-----------+-------+
| RPGRIP1   | 229   |
+-----------+-------+
|   SATB2   | 158   |
+-----------+-------+
|   TBX5    | 156   |
+-----------+-------+
|   ...     | ...   |
+-----------+-------+
|   MAF     |   1   |
+-----------+-------+
|  OCA2     |   1   |
+-----------+-------+


