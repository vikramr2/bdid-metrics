import csv
from datetime import datetime
import networkit as nk
import os
import sys
import time


def main(path_to_edge_list: str, timestamp: str):
    # Time and stopwatch setup
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    start_time = time.time()
    
    if timestamp == "":
        csv_output = f"networkit_bdid-{exec_time}.csv"
    else:
        csv_output = f"networkit_bdid-{timestamp}.csv"

    print("Creating graph in NetworKit...")
    # EdgeList is Tab-Separated and the network's node ID's are 0-indexed
    edgelist_reader = nk.graphio.EdgeListReader("\t", 0, directed=True, continuous=False)
    g = edgelist_reader.read(path_to_edge_list)

    dehydrator = {int(k): v for k, v in edgelist_reader.getNodeMap().items()}
    hydrator = {v: k for k, v in dehydrator.items()}

    read_time = time.time() - start_time
    num_nodes = g.numberOfNodes()
    print(
        f"{g.numberOfEdges()} edges read containing {num_nodes} nodes in {read_time} seconds."
    )

    print("Now computing Bu metrics...")
    print(f"Writing Bu metrics to {csv_output}")

    with open(csv_output, "w") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "fp_int_id",
                "cp_level",
                "cp_r_citing_zero",
                "cp_r_citing_nonzero",
                "tr_citing",
                "cp_r_cited_zero",
                "cp_r_cited_nonzero",
                "tr_cited",
            ],
        )
        writer.writeheader()

        # Compute BDID absolute indicators for all nodes and write node-by-node
        for i, focal_pub in enumerate(g.iterNodes()):
            cp_level = g.degreeIn(focal_pub)
            cp_r_citing_nonzero = 0
            cp_r_cited_nonzero = 0
            tr_citing = 0
            tr_cited = 0

            # If cp_level is zero, everything is zero
            if cp_level == 0:
                writer.writerow(
                    {
                        "fp_int_id": hydrator[focal_pub],
                        "cp_level": 0,
                        "cp_r_citing_zero": 0,
                        "cp_r_citing_nonzero": 0,
                        "tr_citing": 0,
                        "cp_r_cited_zero": 0,
                        "cp_r_cited_nonzero": 0,
                        "tr_cited": 0,
                    }
                )
                continue

            # BDID metrics primarily concerned with a focal pub's in-neighbors
            for citing_pub in g.iterInNeighbors(focal_pub):
                cp_r_citing_flag = False
                cp_r_cited_flag = False
                for neighbor in g.iterNeighbors(citing_pub):
                    # cp_r_citing_nonzero = num citing pubs that also cite other pubs which cite the focal
                    # NOTE: NetworKit does not have an iterOutNeighbors func, so we
                    #   use this logically equivalent conditional.
                    #   Counting edges which cite the citing_pub itself is incorrect.
                    if g.hasEdge(
                        neighbor, focal_pub
                    ) == True and neighbor not in g.iterInNeighbors(citing_pub):
                        tr_citing += 1
                        cp_r_citing_flag = True

                    # cp_r_cited_nonzero = num citing pubs that also cite pubs which the focal_pub cites
                    if g.hasEdge(focal_pub, neighbor) == True:
                        tr_cited += 1
                        cp_r_cited_flag = True

                # Increment the corresponding metric for the focal pub if citing_pub
                #   met the corresponding conditions above
                if cp_r_citing_flag:
                    cp_r_citing_nonzero += 1
                if cp_r_cited_flag:
                    cp_r_cited_nonzero += 1

            # The sum of the _zero and _nonzero indicators must equal cp_level
            cp_r_citing_zero = cp_level - cp_r_citing_nonzero
            cp_r_cited_zero = cp_level - cp_r_cited_nonzero

            writer.writerow(
                {
                    "fp_int_id": hydrator[focal_pub],
                    "cp_level": cp_level,
                    "cp_r_citing_zero": cp_r_citing_zero,
                    "cp_r_citing_nonzero": cp_r_citing_nonzero,
                    "tr_citing": tr_citing,
                    "cp_r_cited_zero": cp_r_cited_zero,
                    "cp_r_cited_nonzero": cp_r_cited_nonzero,
                    "tr_cited": tr_cited,
                }
            )

            if (i + 1) % 10000 == 0:
                print(
                    f"{i+1} / {num_nodes} nodes calculated...\nTotal time elapsed: {time.time() - start_time} seconds..."
                )

    finish_time = time.time() - start_time
    print(f"Completed calculating BDID for {num_nodes} nodes in {finish_time} seconds.")
    print(f"Output file location: {csv_output}")


if __name__ == "__main__":
    num_args = len(sys.argv)
    if num_args != 2 and num_args != 3:
        print("Invalid number of arguments. See usage below:")
        print("Usage: traditional_bdid_networkit.py path_to_edge_list [timestamp]")
        print("\tArguments:")
        print("\t\tpath_to_edge_list: Path to the TSV containing the list of edges.")
        print("\t\ttimestamp: Optional. Specifies the timestamp suffix for the output file.")
        print("\t\t\tDefaults to the timestamp of this script's execution.")
        exit(1)

    # Check validity of input path
    if os.path.exists(sys.argv[1]) == False:
        print(
            "The specified path_to_edge_list could not be found. Please check the file name and try again."
        )
        exit(1)

    # Use the timestamp if provided, otherwise signal to main to generate one
    if num_args == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main(sys.argv[1], "")
