# Python Version of Clustered BDID data collection

## Relevant Files
- [`collect_bdid_clustered.py`](collect_clustered.py)
    - Computes the clustered BDID metrics on the specified input clustering file and edge list.
    - Usage: `python3 collect_bdid_clustered.py path_to_clustering_file path_to_edge_list [num_workers]`
- [bdid_10_column.py](bdid_10_column.py)
    - Merges the traditional and clustered BDID metrics together into one output CSV. Because it uses natural joins, if either one of the input CSVs are missing integer_id rows that the other has, it is dropped from the resulting CSV.
    - May be deprecated after pipeline optimizations, as both traditional and clustered metrics will then be calculated in the same process.
- [`csv_writer.py`](csv_writer.py)
    - Custom module used as a dependency in [`collect_bdid_clustered.py`](collect_clustered.py).
    - Worker process class that writes metrics to CSV output as workers compute them.
- [`worker.py`](worker.py)
    - Custom module used as a dependency in [`collect_bdid_clustered.py`](collect_clustered.py).
    - Worker process class that computes metrics.
- [`log_listener.py`](log_listener.py)
    - Custom module used as a dependency in [`collect_bdid_clustered.py`](collect_clustered.py).
    - Logger process class that writes to a logfile for debugging and script performance analytics.

## Running this part of the Pipeline (DEPRECATED)
This folder contains the scripts and modules used to calculate the clustered BDID metrics. To run this part of the pipeline, run `nohup python3 collect_clustered_full.py <NUM_WORKERS>` where NUM_WORKERS is the number of parallel workers to use. I suggest this number to be about half of the amount of RAM your system has. 

## Running the data visualization scripts
This folder also contains data visualization scripts. See the Relevant Files section above.

## Inputs Tested On
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
