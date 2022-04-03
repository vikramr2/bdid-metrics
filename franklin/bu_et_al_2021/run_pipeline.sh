#!/bin/bash
: '
This script runs the full Bu and Bu-Plus pipeline with the given input arguments.
We expect the first arg ($1) to be the path to the edge list TSV,
    and the second arg ($2) to be the path to the clustering file CSV.
    Exceptions will be thrown by the Python scripts if the files are not of their respective formats,
    and the pipeline will be stopped.

The output files will be placed in the directory where the pipeline was called from.
    The runtime timestamp ($exec_time) will be noted to title the output files.
    - The Bu CSV will be saved as networkit_bdid-$exec_time with $exec_time being the timestamp.
    - The Bu-Plus CSV will be saved as networkit_clustered_bdid-$exec_time with $exec_time being the timestamp.
    - The final 10 column CSV will be saved as bu_10_column-$exec_time with $exec_time being the timestamp.

Example script usage (runs pipeline with no hangup signal and tracks pipeline runtime):
    nohup time bash run_pipeline.sh path_to_edge_list path_to_clustering_file
'

# Grab the runtime timestamp and use it as a suffix for the output files
exec_time=$(date '+%Y-%m-%d-%H-%M-%S')
traditional_expected_out="networkit_bdid-$exec_time.csv"
clustered_expected_out="networkit_clustered_bdid-$exec_time.csv"

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

# Craft the arguments for each stage as an array and then pass it to each stage call
stage_one_args=($1 $exec_time)
stage_two_args=($1 $2 $exec_time)
stage_three_args=($traditional_expected_out $clustered_expected_out $exec_time)

echo -e "Running BDID Pipeline Stage 1/3:\npython3 pipeline/traditional_bdid_networkit.py $1 $exec_time"

# Run stage and stop pipeline if an error occurred in the previous script
if ! python3 pipeline/traditional_bdid_networkit.py ${stage_one_args[*]}; then
    echo -e "An error occurred while executing python3 pipeline/traditional_bdid_networkit.py $1 $exec_time\nPipeline killed at Stage 1/3."
    exit 1
fi

echo "Finished Stage 1/3."
echo -e "Running BDID Pipeline Stage 2/3:\npython3 pipeline/clustered_bdid_networkit.py $1 $2 $exec_time"

if ! python3 pipeline/clustered_bdid_networkit.py ${stage_two_args[*]}; then
    echo -e "An error occurred while executing python3 pipeline/clustered_bdid_networkit.py $1 $2 $exec_time\nPipeline killed at Stage 2/3."
    exit 1
fi

echo "Finished Stage 2/3."
echo -e "Running BDID Pipeline Stage 3/3:\npython3 pipeline/create_10_column.py $traditional_expected_out $clustered_expected_out $exec_time"

if ! python3 pipeline/create_10_column.py ${stage_three_args[*]}; then
    echo -e "An error occurred while executing python3 pipeline/create_10_column.py $traditional_expected_out $clustered_expected_out $exec_time\nPipeline killed at Stage 3/3."
    exit 1
fi

echo "Finished Stage 3/3."
echo "BDID Pipeline Finished Successfully."
