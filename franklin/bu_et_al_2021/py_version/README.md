# Python Version of BDID data collection

## Running this part of the Pipeline
This folder contains the script used to collect the standard Bu metrics. Optimizations for this part of the pipeline are currently in the works. To run this part of the pipeline, simply run `nohup python3 full_scale_bdid.py <NUM_WORKERS>` where NUM_WORKERS is the number of parallel workers to use. I suggest this number to be about half of the amount of RAM your system has.

Usage: `python3 full_scale_bdid.py`

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
