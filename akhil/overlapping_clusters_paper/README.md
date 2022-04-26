# Overlapping CLustering Paper Contents

## Overlapping KMP Pipeline

This program runs the step 5 of the OKMP method and saves it to your local directory. To run this program, 
run the following code. 

``console
python3 overlapping_kmp_pipeline.py --network-file [path to tsv network file] --clustering [path to input kmp-valid disjoint clustering csv file]
-- output-path [path to save outputted overlapping clustering] --min-k-core [min k of input clustering] --top-percent [top n percent of candidate nodes to consider adding]
-- inclusion-criterion [k, mcd] --marker-file [marker csv file to run analysis with]
```

## Visualization

Utility file to run histogram analysis or scatterplot analysis on clusterings


## Overlapping Clustering Stats

Utility file ot run other analysis on clustering files outputted from the Pipeline


## Utils

Various utility functions that may be needed in preprocessing data


