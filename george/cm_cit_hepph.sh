#!/bin/bash

# Workflow for processing Leiden clusterings with
# tree and size filters then connectivity modifier
# then tree and size filters again. 12/25/2022
# George Chacko

# This script is designed to be compatible with other networks
# in the same directory hierarchy, e.g., find and replace
# cit_patents with orkut or cen or wtp

echo "Starting now..."

set -e

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting

trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

# Setup
echo "Activating python venv"
cd /data1/snap_leiden_venv
source ./bin/activate
cd /data1/snap_leiden_venv/cit_hepph/

# Filter for trees and size
echo "Filtering trees and small clusters..."
python analyze_cit_hepph.py

# Connectivity Modifier. Input network has been cleaned to remove duplicate and  parallel edges as well as self loops
echo "*** Running CM ***"
cm -i ./cit_hepph_cleaned.tsv -c leiden  -g 0.5 -t 1log10  -e cit_hepph_leiden.5_nontree_n10_clusters.tsv -o cit_hepph_leiden.5_preprocessed_cm.out.tsv
echo "***"
cm -i ./cit_hepph_cleaned.tsv -c leiden  -g 0.1 -t 1log10  -e cit_hepph_leiden.1_nontree_n10_clusters.tsv -o cit_hepph_leiden.1_preprocessed_cm.out.tsv
echo "***"
cm -i ./cit_hepph_cleaned.tsv -c leiden  -g 0.01 -t 1log10  -e cit_hepph_leiden.01_nontree_n10_clusters.tsv -o cit_hepph_leiden.01_preprocessed_cm.out.tsv
echo "***"
cm -i ./cit_hepph_cleaned.tsv -c leiden  -g 0.001 -t 1log10  -e cit_hepph_leiden.001_nontree_n10_clusters.tsv -o cit_hepph_leiden.001_preprocessed_cm.out.tsv
echo "*** *** ***"

# Stage 2 of Connectivity modifier 

echo "*** Running CM Universal ***"
cm2universal -g cit_hepph_cleaned.tsv -i cit_hepph_leiden.5_preprocessed_cm.out.tsv -o cit_hepph_leiden.5_preprocessed_cm.out.tsv
cm2universal -g cit_hepph_cleaned.tsv -i cit_hepph_leiden.1_preprocessed_cm.out.tsv -o cit_hepph_leiden.1_preprocessed_cm.out.tsv
cm2universal -g cit_hepph_cleaned.tsv -i cit_hepph_leiden.01_preprocessed_cm.out.tsv -o cit_hepph_leiden.01_preprocessed_cm.out.tsv
cm2universal -g cit_hepph_cleaned.tsv -i cit_hepph_leiden.001_preprocessed_cm.out.tsv -o cit_hepph_leiden.001_preprocessed_cm.out.tsv

# convert json output to tsv 
echo "*** Running json2membership.py to convert json to tsv"
python3 /data1/snap_leiden_venv/json2membership.py -i cit_hepph_leiden.5_preprocessed_cm.out.tsv.after.json  -o cit_hepph_leiden.5_after.tsv
python3 /data1/snap_leiden_venv/json2membership.py -i cit_hepph_leiden.1_preprocessed_cm.out.tsv.after.json  -o cit_hepph_leiden.1_after.tsv
python3 /data1/snap_leiden_venv/json2membership.py -i cit_hepph_leiden.01_preprocessed_cm.out.tsv.after.json  -o cit_hepph_leiden.01_after.tsv
python3 /data1/snap_leiden_venv/json2membership.py -i cit_hepph_leiden.001_preprocessed_cm.out.tsv.after.json  -o cit_hepph_leiden.001_after.tsv

# filter for trees and size again
echo "Round 2 filter for trees and small clusters"
python analyze_cit_hepph_r2.py
# collate using R
echo "Assemble df using R"
Rscript analyze_cit_hepph.R

# copy to staging area
echo "Copy to assemble folder"
cp cit_hepph_cm_df.csv ../assemble

echo "*** *** *** *** *** ***" 
echo "DONE DONE DONE"
echo "*** *** *** *** *** ***

