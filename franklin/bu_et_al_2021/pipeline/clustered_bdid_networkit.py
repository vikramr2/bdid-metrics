import csv
from datetime import datetime
import networkit as nk
import os
import pandas as pd
import sys
import time


def main(path_to_edge_list: str, path_to_clustering_file: str):
    # Time and stopwatch setup
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    start_time = time.time()
    csv_output = f"networkit_clustered_bdid-{exec_time}.csv"

    # TODO: Either merge this into the traditional_bdid_networkit version
    #   when done, or create the pipeline by calling these from a bash script.

    print("Creating Pandas Dataframes for input files...", end=" ", flush=True)
    # Intake clustering CSV into a Pandas DataFrame
    # NOTE: Node IDs are 0-indexed while cluster IDs are 1-indexed
    #       Both of these IDs are continuous. This means that if there are
    #           K IDs, then the assigned IDs go from 0 to K-1, inclusive.
    df_clusters = pd.read_csv(
        path_to_clustering_file,
        names=["citing_int_id", "citing_cluster_id"],
    )

    # Intake edge list TSV into a Pandas DataFrame
    df_edges = pd.read_csv(
        path_to_edge_list,
        sep="\t",
        names=["citing_int_id", "cited_int_id"],
    )

    print(
        "Done!\nFinished Traditional BDID dataframes. Now building Clustered BDID dataframes...",
        end = " ", flush=True
    )

    # Put edge list with each endpoint's cluster_id into a dataframe
    # Note that some edges will be lost if either or both of its
    #   endpoints were part of kmp-invalid clusters
    #   (if kmp-invalid, they don't exist in the clustering file)
    df_edges_clustered = pd.read_csv(
        path_to_edge_list,
        sep="\t",
        names=["citing_int_id", "cited_int_id"],
    )
    df_edges_clustered = df_edges_clustered.merge(
        df_clusters, on="citing_int_id", how="inner"
    )
    df_clusters.rename(
        columns={
            "citing_int_id": "cited_int_id",
            "citing_cluster_id": "cited_cluster_id",
        },
        inplace=True,
    )
    df_edges_clustered = df_edges_clustered.merge(
        df_clusters, on="cited_int_id", how="inner"
    )
    df_clusters.rename(
        columns={"cited_int_id": "pub_int_id", "cited_cluster_id": "pub_cluster_id"},
        inplace=True,
    )

    dataframe_finish_time = time.time()
    print("Done!")
    print("Edge list read:")
    print(df_edges)
    print("Clustering list read:")
    print(df_clusters)
    print("Clustered edge list:")
    print(df_edges_clustered)
    print(f"Dataframes created in {dataframe_finish_time - start_time} seconds.")

    # NOTE: 2 Possible approaches
    #   1. For each cluster, make a new NetworKit graph that also only contains
    #       intra-cluster edges. Then for each node in the cluster, calculate
    #       the BDID metrics.
    #       (Easier to implement but can be slow as you build new graphs each time.
    #        Is this method more memory efficient because the graphs are smaller?)
    #   2. Make the entire exosome network as a NetworKit graph while also
    #       creating some data structures to keep track of clustering.
    #       (Could just use the Pandas DF and do queries)
    #       Then for each node, check for existence of BDID edges
    #       for all nodes in the clustering data structure.
    #       Using Pandas df.query() is faster than using truth arrays.
    #       (Won't need to build new graph each time, but this seems like a lot of work
    #        Seems like this may take up more memory than approach 1...)

    # NOTE: Using Approach 1
    min_cluster_id = df_clusters["pub_cluster_id"].min()
    max_cluster_id = df_clusters["pub_cluster_id"].max()

    print("Now computing Bu-Plus metrics...")
    with open(csv_output, "w") as output_file:

        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "fp_int_id",
                "cp_level_clustered",
                "cp_r_citing_zero_clustered",
                "cp_r_citing_nonzero_clustered",
                "tr_citing_clustered",
                "cp_r_cited_zero_clustered",
                "cp_r_cited_nonzero_clustered",
                "tr_cited_clustered",
            ],
        )
        writer.writeheader()

        # Iterate through all of the clusters
        for cluster_id in range(min_cluster_id, max_cluster_id + 1):
            # Filter to only include intra-cluster nodes and edges
            intra_cluster_edges_df = df_edges_clustered.query(
                f"citing_cluster_id == {cluster_id} and cited_cluster_id == {cluster_id}"
            )
            intra_cluster_nodes_df = df_clusters.query(
                f"pub_cluster_id == {cluster_id}"
            )

            # Create a new graph with only the intra_cluster nodes and edges
            cluster_graph = nk.graph.Graph(directed=True)
            for _, row in intra_cluster_edges_df.iterrows():
                cluster_graph.addEdge(
                    row["citing_int_id"], row["cited_int_id"], addMissing=True
                )

            # Calculate Bu-Plus metrics for each node in the cluster
            for _, row in intra_cluster_nodes_df.iterrows():
                focal_pub = row["pub_int_id"]
                cp_level_clustered = cluster_graph.degreeIn(focal_pub)
                cp_r_citing_nonzero_clustered = 0
                cp_r_cited_nonzero_clustered = 0
                tr_citing_clustered = 0
                tr_cited_clustered = 0

                # If cp_level is zero, everything is zero
                if cp_level_clustered == 0:
                    writer.writerow(
                        {
                            "fp_int_id": focal_pub,
                            "cp_level_clustered": 0,
                            "cp_r_citing_zero_clustered": 0,
                            "cp_r_citing_nonzero_clustered": 0,
                            "tr_citing_clustered": 0,
                            "cp_r_cited_zero_clustered": 0,
                            "cp_r_cited_nonzero_clustered": 0,
                            "tr_cited_clustered": 0,
                        }
                    )
                    continue

                # BDID metrics primarily concerned with a focal pub's in-neighbors
                for citing_pub in cluster_graph.iterInNeighbors(focal_pub):
                    cp_r_citing_flag = False
                    cp_r_cited_flag = False
                    for neighbor in cluster_graph.iterNeighbors(citing_pub):
                        # cp_r_citing_nonzero = num citing pubs that also cite other pubs which cite the focal.
                        # NOTE: NetworKit does not have an iterOutNeighbors func,
                        #         so we also have to check if the neighbor is
                        #         one of citing_pub's in-neighbors.
                        #         Counting edges which cite the citing_pub is incorrect.
                        if (
                            cluster_graph.hasEdge(neighbor, focal_pub) == True
                            and neighbor not in cluster_graph.iterInNeighbors(citing_pub)
                        ):
                            tr_citing_clustered += 1
                            cp_r_citing_flag = True

                        # cp_r_cited_nonzero = num citing pubs that also cite pubs which the focal_pub cites
                        if cluster_graph.hasEdge(focal_pub, neighbor) == True:
                            tr_cited_clustered += 1
                            cp_r_cited_flag = True

                    # Increment the corresponding metric for the focal pub if citing_pub
                    #   met the corresponding conditions above
                    if cp_r_citing_flag:
                        cp_r_citing_nonzero_clustered += 1
                    if cp_r_cited_flag:
                        cp_r_cited_nonzero_clustered += 1

                # The sum of the _zero and _nonzero indicators must equal cp_level
                cp_r_citing_zero_clustered = (
                    cp_level_clustered - cp_r_citing_nonzero_clustered
                )
                cp_r_cited_zero_clustered = (
                    cp_level_clustered - cp_r_cited_nonzero_clustered
                )

                writer.writerow(
                    {
                        "fp_int_id": focal_pub,
                        "cp_level_clustered": cp_level_clustered,
                        "cp_r_citing_zero_clustered": cp_r_citing_zero_clustered,
                        "cp_r_citing_nonzero_clustered": cp_r_citing_nonzero_clustered,
                        "tr_citing_clustered": tr_citing_clustered,
                        "cp_r_cited_zero_clustered": cp_r_cited_zero_clustered,
                        "cp_r_cited_nonzero_clustered": cp_r_cited_nonzero_clustered,
                        "tr_cited_clustered": tr_cited_clustered,
                    }
                )

            if cluster_id % 1000 == 0:
                print(
                    f"{cluster_id} / {max_cluster_id} clusters calculated...\nTotal time elapsed: {time.time() - start_time} seconds..."
                )

    finish_time = time.time() - start_time
    print(
        f"Completed calculating BDID for {max_cluster_id} clusters in {finish_time} seconds."
    )
    print(f"Output file location: {csv_output}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid number of arguments. See usage below:")
        print(
            "Usage: traditional_bdid_networkit.py path_to_edge_list path_to_clustering_file"
        )
        print("\tArguments:")
        print("\t\tpath_to_edge_list: Path to the TSV containing the list of edges.")
        print(
            "\t\tpath_to_clustering_file: Path to the CSV containing clustering info."
        )
        exit(1)

    # Check validity of inputs
    if os.path.exists(sys.argv[1]) == False:
        print(
            "The specified path_to_edge_list could not be found. Please check the file name and try again."
        )
        exit(1)
    if os.path.exists(sys.argv[2]) == False:
        print(
            "The specified path_to_clustering_file could not be found. Please check the file name and try again."
        )
        exit(1)

    main(sys.argv[1], sys.argv[2])
