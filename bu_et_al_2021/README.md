# Bu's Breadth/Depth and Independence/Dependence (BDID) Calculations

## What are Bu and Bu-Plus metrics?
***Bu et al. (2021)*** proposed a new method of quantifying citation impact for research publications. These proposed metrics are breadth, depth, independence, and dependence. **Bu-Plus** takes these metrics and considers them at a cluster level by only considering edges which are part of a publication's clustering in the network.

## Input Graph
When this dataset was created, we used the exosome citation network provided by Dimensions. In this graph, each node is a publication (which is assigned an integer ID for internal reference), and each edge is a directed edge representing citations, meaning that the node at the tail of the edge cites the node at the head of the edge. The edge list was used to create the graph and calculate the Bu metrics. 

As described in ***Wedell et al. (2021)***, the exosome citation network was clustered using various different network clustering algorithms. For the **Bu-Plus** data in this folder, the k=5 p=2 recursive graclus clustering of the network was used.

## Running the Pipeline
The pipeline script [`run_pipeline.sh`](run_pipeline.sh) runs the full Bu and Bu-Plus pipeline with the given input arguments.
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

## Directories
- [`deprecated_version`](deprecated_version)
    - Contains all of the initial PL/pgSQL and Pandas scripts used to generate the initial Bu and Bu-Plus metrics.
- [`pipeline`](pipeline)
    - Contains the Python scripts for each stage of the Bu and Bu-Plus 3-stage data pipeline.

## Files
- [`compare_bdid_csvs.py`](compare_bdid_csvs.py)
    - Python scripts that checks to see if the two input CSVs contain the same BDID data for nodes that they both have data for.
    - Usage: `python3 compare_bdid_csvs.py csv_one csv_two` 
- [`plot_bdid_ratios.py`](plot_bdid_ratios.py)
    - Creates scatter and density plots of the ratios of the clustered Bu metrics to their traditional Bu counterparts and saves them.
    - **Currently uses hard-coded file paths**.
    - Usage: `python3 plot_bdid_ratios.py`
- [`plot_bdid_vs_level.py`](plot_bdid_vs_levels.py)
    - Creates scatter plots of the traditional and the clustered Bu metrics.
    - **Currently uses hard-coded file paths**.
    - Usage: `python3 plot_bdid_vs_level.py`