# How to run the script:
Copy the Leiden folder into this folder. Then:
```console
$ python graph_write.py
$ python input.py --network output.csv --output-prefix ./mapping/
$ java -cp ./leiden/leiden.jar nl.cwts.networkanalysis.run.RunNetworkClustering -r 0.3 -o output_leiden.clusters leiden_prep.tsv
$ cat output_leiden.clusters
```

