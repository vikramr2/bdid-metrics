# Bu and Bu-Plus BDID NetworKit Pipeline Files
This directory contains the scripts used by the pipeline in the next directory up.

## Scripts
Each of the following scripts are called from the pipeline script in the next higher directory. However, they can also be run independently using their respective usage statements:
- [`traditional_bdid_networkit.py`](traditional_bdid_networkit.py)
    - Usage: `traditional_bdid_networkit.py path_to_edge_list [timestamp]`
        - `path_to_edge_list`: Path to the TSV containing the list of edges.
        - `timestamp`: Optional. Specifies the timestamp suffix for the output file. Defaults to the timestamp of this script's execution.
    - Stage 1 of the Pipeline.
    - Reads the input network edge list and generates the Bu metrics for the network.
- [`clustered_bdid_networkit.py`](clustered_bdid_networkit.py)
    - Usage: `clustered_bdid_networkit.py path_to_edge_list path_to_clustering_file [timestamp]`
        - `path_to_edge_list`: Path to the TSV containing the list of edges.
        - `path_to_clustering_file`: Path to the CSV containing clustering info.
        - `timestamp`: Optional. Specifies the timestamp suffix for the output file. Defaults to the timestamp of this script's execution.
    - Stage 2 of the pipeline.
    - Reads the input clustered network from the input file paths `path_to_edge_list` and `path_to_clustering_file` and generates the Bu-Plus metrics for the network.
- [`create_10_column.py`](create_10_column.py)
    - Usage: `create_10_column.py csv_one csv_two [timestamp]`
        - `csv_one`: Path to the left CSV to merge to create the 10 column CSV.
        - `csv_two`: Path to the right CSV to merge to create the 10 column CSV.
        - `timestamp`: Optional. Specifies the timestamp suffix for the output file. Defaults to the timestamp of this script's execution.
    - Stage 3 of the pipeline.
    - Creates a CSV from the inner join on the focal publication integer ID of the Bu and Bu-Plus metrics.

## Running the Pipeline
The pipeline script [`run_pipeline.sh`](../run_pipeline.sh) runs the full Bu and Bu-Plus pipeline with the given input arguments.
We expect the first arg to be the path to the edge list TSV,
    and the second arg ($2) to be the path to the clustering file CSV.
    Exceptions will be thrown by the Python scripts if the files are not of their respective formats,
    and the pipeline will be stopped.

The pipeline runs in three stages:
1. Collect and export Bu metrics on the input.
2. Collect and export Bu-Plus metrics on the input.
3. Inner join the Bu and Bu-Plus metrics from the earlier stages.

The output files will be placed in the directory where the pipeline was called from.
    The runtime timestamp ($exec_time) will be noted to title the output files.
- The Bu CSV will be saved as networkit_bdid-$exec_time with $exec_time being the timestamp.
- The Bu-Plus CSV will be saved as networkit_clustered_bdid-$exec_time with $exec_time being the timestamp.
- The final 10 column CSV will be saved as bu_10_column-$exec_time with $exec_time being the timestamp.

Example script usage (runs pipeline with no hangup signal and tracks pipeline runtime):
    
`nohup bash run_pipeline.sh path_to_edge_list path_to_clustering_file`

## Helpful resources
- [Reading an EdgeList into NetworKit](https://networkit.github.io/dev-docs/notebooks/IONotebook.html#EdgeList-file-format)
- [NetworKit Python API](https://networkit.github.io/dev-docs/python_api/)