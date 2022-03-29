#!/bin/bash
: '
This script runs the full Bu and Bu-Plus pipeline with the given input arguments.
We expect the first arg ($1) to be the path to the edge list TSV,
    and the second arg ($2) to be the path to the clustering file CSV.
    Exceptions will be thrown by the Python scripts if the files are not of their respective formats,
    and the pipeline will be stopped.

Example script usage:
    bash run_pipeline.sh path_to_edge_list path_to_clustering_file
'

# Ensure that the number of args is correct
if [ $# -ne 2 ]; then
    echo -e "Incorrect number of arguments. See usage statement below:"
    echo -e "Usage: run_pipeline.sh path_to_edge_list path_to_clustering_file"
    echo -e "\tArguments:"
    echo -e "\t\tpath_to_edge_list: Path to the TSV containing the list of edges in the network."
    echo -e "\t\tpath_to_clustering_file: Path to the CSV containing the clusterings."
    exit 1
fi

# Verify existence of input files
if [ ! -f "$1" ]; then
    echo "The input path_to_edge_list could not be found. Please check the file name and try again."
    exit 1
fi

if [ ! -f "$2" ]; then
    echo "The input path_to_clustering_file could not be found. Please check the file name and try again."
    exit 1
fi

echo -e "Starting BDID Pipeline Stage 1/2:\npython3 pipeline/traditional_bdid_networkit.py $1"
# python3 pipeline/traditional_bdid_networkit.py $1

# Stop pipeline if an error occurred in the previous script
if [ $? -ne 0 ]; then
    echo -e "An error occurred while executing python3 pipeline/traditional_bdid_networkit.py $1.\nPipeline stopped."
    exit 1
fi

echo -e "Starting BDID Pipeline State 2/2:\npython3 pipeline/clustered_bdid_networkit.py $1 $2"
python3 pipeline/clustered_bdid_networkit.py $1 $2

# Stop pipeline if an error occurred in the previous script
if [ $? -ne 0 ]; then
    echo -e "An error occurred while executing python3 pipeline/clustered_bdid_networkit.py $1.\nPipeline stopped."
    exit 1
fi

echo "BDID Pipeline Finished."
