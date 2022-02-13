# Python Version of BDID data collection
## Relevant Files
- /srv/local/shared/external/clusterings/exosome_1900_2010_sabpq/IKC+RG+Aug+kmp-parse/ikc-rg-aug_k_5_p_2.clustering
    - CSV format
    - First col is node_id
    - Second col is cluster_id

- /srv/local/shared/external/dbid/franklins_sample.csv
    - First col (V2) appears to be cluster_id
    - Second col (V1) appears to be node_id
    - Third col (N) appears to be number of nodes in cluster cluster_id
    - Last col (gp) appears to be cluster_id's quartile

- /srv/local/shared/external/for_eleanor/gc_exosome/citing_cited_network.integer.tsv
    - Master edge list
    - First column is citing_int_id, second is cited_int_id
    - TSV = Tab Separated Values ('\t')
