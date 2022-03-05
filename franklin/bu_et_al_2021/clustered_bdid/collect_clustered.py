# Utility Imports
import csv
from datetime import datetime
import sys
import time

import pandas as pd

from multiprocessing import Manager, Process, Queue, current_process

import logging
import logging.handlers


class Worker(Process):
    """Worker that calculates the BDID metrics for items in queue"""

    def __init__(
        self,
        nodes_to_calc: Queue,
        calculated_tuples: Queue,
        nodes_read: int,
        df_edges: pd.DataFrame,
        log_queue: Queue,
    ):
        super().__init__(daemon=True)
        self.nodes_to_calc = nodes_to_calc
        self.calculated_tuples = calculated_tuples
        self.nodes_read = nodes_read
        self.df_edges = df_edges
        self.log_queue = log_queue

    def run(self):
        logger = logging.getLogger("Logger")

        while True:

            next_node = self.nodes_to_calc.get()

            if next_node is None:
                self.nodes_to_calc.put_nowait(None)
                self.nodes_to_calc.close()
                print(f"Process {current_process().pid} is ready to join.")
                break

            focal_int_id = next_node[0]
            cluster_id = next_node[1]

            print(
                f"Process {current_process().pid} has started pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue)"
            )

            # Get all edges where the cited_int_id is the focal
            focal_incoming_edges = self.df_edges.loc[
                (self.df_edges["cited_int_id"] == focal_int_id)
            ]
            cp_level = len(focal_incoming_edges.index)

            # Get focal_pub's outgoing edges
            focal_outgoing_edges = self.df_edges.loc[
                (self.df_edges["citing_int_id"] == focal_int_id)
            ]
            num_cited_references = len(focal_outgoing_edges.index)

            # Get the nodes edges coming into FP from nodes from the same cluster
            citing_edges_from_same_cluster = focal_incoming_edges.loc[
                (focal_incoming_edges["citing_cluster_id"] == cluster_id)
            ]
            num_citing_edges_from_same_cluster = len(
                citing_edges_from_same_cluster.index
            )
            citing_nodes_from_same_cluster = (
                citing_edges_from_same_cluster.drop_duplicates(subset=["citing_int_id"])
            )
            num_citing_nodes_from_same_cluster = len(
                citing_nodes_from_same_cluster.index
            )

            # Get the edges going from FP to other nodes in the same cluster
            cited_nodes_from_same_cluster = focal_outgoing_edges.loc[
                (focal_outgoing_edges["cited_cluster_id"] == cluster_id)
            ]
            num_cited_nodes_from_same_cluster = len(cited_nodes_from_same_cluster.index)

            # Get the edges where the citing_int_id also cites
            # another pub that cites focal_int_id
            bread_depth_df = self.df_edges.loc[
                (
                    self.df_edges["citing_int_id"].isin(
                        focal_incoming_edges["citing_int_id"]
                    )
                    & self.df_edges["cited_int_id"].isin(
                        focal_incoming_edges["citing_int_id"]
                    )
                )
            ]

            # Get the edges where the citing_int_id also cites the
            # pubs that focal_pub cites
            ind_dep_df = self.df_edges.loc[
                (
                    self.df_edges["citing_int_id"].isin(
                        focal_incoming_edges["citing_int_id"]
                    )
                    & self.df_edges["cited_int_id"].isin(
                        focal_outgoing_edges["cited_int_id"]
                    )
                )
            ]

            # Get the number of breadth/depth edges where both ends are from the same cluster
            clustered_bread_depth = bread_depth_df.loc[
                (
                    (bread_depth_df["citing_cluster_id"] == cluster_id)
                    & (bread_depth_df["cited_cluster_id"] == cluster_id)
                )
            ]
            tr_citing_both_from_same_cluster = len(clustered_bread_depth.index)

            # Get the number of ind/dep edges where both ends are from the same cluster
            clustered_ind_dep = ind_dep_df.loc[
                (
                    (ind_dep_df["citing_cluster_id"] == cluster_id)
                    & (ind_dep_df["cited_cluster_id"] == cluster_id)
                )
            ]
            tr_cited_both_from_same_cluster = len(clustered_ind_dep.index)

            # Get the unique citing_ids for each dataframe
            unique_citing_ids_clustered_bread_depth = (
                clustered_bread_depth.drop_duplicates(subset=["citing_int_id"])
            )
            unique_citing_ids_clustered_ind_dep = clustered_ind_dep.drop_duplicates(
                subset=["citing_int_id"]
            )

            cp_citing_nonzero_from_same_cluster = len(
                unique_citing_ids_clustered_bread_depth.index
            )
            cp_cited_nonzero_from_same_cluster = len(
                unique_citing_ids_clustered_ind_dep.index
            )

            # Format data tuple to send back to the main process
            tup = (
                focal_int_id,
                cluster_id,
                cp_level,
                num_cited_references,
                num_citing_edges_from_same_cluster,
                num_citing_nodes_from_same_cluster,
                num_cited_nodes_from_same_cluster,
                tr_citing_both_from_same_cluster,
                tr_cited_both_from_same_cluster,
                cp_citing_nonzero_from_same_cluster,
                cp_cited_nonzero_from_same_cluster,
            )

            self.calculated_tuples.put(tup)

            print(
                f"Process {current_process().pid} has finished pub {focal_int_id} ({self.calculated_tuples.qsize()} / {self.nodes_read} finished)"
            )
            if self.nodes_to_calc.qsize() % 1000 == 0:
                logger.log(
                    logging.INFO,
                    f"{self.calculated_tuples.qsize()} / {self.nodes_read} nodes calculated.",
                )


class LogListener(Process):
    """Listener class that handles logging info for the worker processes"""

    def __init__(self, listen_queue: Queue, logfile_name: str):
        super().__init__(daemon=True)
        self.listen_queue = listen_queue
        self.logfile_name = logfile_name

    def run(self):
        # Set up logfile
        root = logging.getLogger()
        h = logging.handlers.RotatingFileHandler(self.logfile_name, "a")
        f = logging.Formatter(
            "%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s"
        )
        h.setFormatter(f)
        root.addHandler(h)
        while True:
            next_message = self.listen_queue.get()
            if next_message is None:
                break
            logger = logging.getLogger(next_message.name)
            logger.handle(next_message)


def main(max_cores: int = 8):

    # Format names of output files
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    start_time = time.time()
    csv_output = f"fmoy3_clustered_bdid-{exec_time}.csv"
    logfile_output = f"logfile_clustered_bdid_{exec_time}.txt"

    # Spin up logging process
    log_queue = Queue()
    log_listener = LogListener(log_queue, logfile_output)
    log_listener.start()
    h = logging.handlers.QueueHandler(log_queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)
    logger = logging.getLogger("Logger")

    print(
        f"Entered main function:\nWill generate output in {csv_output} and log to {logfile_output}"
    )
    logger.log(
        logging.INFO, f"Entered main function: Will generate output in {csv_output}"
    )
    print(f"Using {max_cores} CPU cores...")
    logger.log(logging.INFO, f"Using {max_cores} CPU cores...")

    print("Generating dataframes. This will take a minute...")
    logger.log(logging.INFO, "Generating dataframes. This will take a minute...")

    # Create a copy of the edge list into a Pandas Dataframe
    df_edges = pd.read_csv(
        "/srv/local/shared/external/for_eleanor/gc_exosome/citing_cited_network.integer.tsv",
        sep="\t",
        names=["citing_int_id", "cited_int_id"],
    )

    print(f"Initial edges dataframe:\n{df_edges}")
    logger.log(logging.INFO, f"\nInitial edges dataframe:\n{df_edges}")

    # Read the clusterings as a dataframe and perform natural joins
    df_clusters = pd.read_csv(
        "/srv/local/shared/external/clusterings/exosome_1900_2010_sabpq/IKC+RG+Aug+kmp-parse/ikc-rg-aug_k_5_p_2.clustering",
        names=["citing_int_id", "citing_cluster_id"],
    )
    df_edges = df_edges.merge(df_clusters, on="citing_int_id", how="inner")
    df_clusters = pd.read_csv(
        "/srv/local/shared/external/clusterings/exosome_1900_2010_sabpq/IKC+RG+Aug+kmp-parse/ikc-rg-aug_k_5_p_2.clustering",
        names=["cited_int_id", "cited_cluster_id"],
    )
    df_edges = df_edges.merge(df_clusters, on="cited_int_id", how="inner")

    print(f"Joined dataframe:\n{df_edges}")
    logger.log(logging.INFO, f"\nJoined dataframe:\n{df_edges}")
    print("Done!")
    logger.log(logging.INFO, "Done!")
    print("Reading node list...")
    logger.log(logging.INFO, "Reading node list")

    # Read in the node list and prepare child processes (currently using the sample)
    nodes_to_calc = Queue()
    manager = Manager()
    # Must use a manager-based queue as it is able to handle more than 64 child processes
    calculated_tuples = manager.Queue()
    nodes_calculated = 0
    with open("/srv/local/shared/external/dbid/franklins_sample.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            nodes_to_calc.put((int(row["V1"]), int(row["V2"])))

    nodes_read = nodes_to_calc.qsize()
    nodes_to_calc.put(None)
    print(f"Done! {nodes_read} nodes read.")
    logger.log(logging.INFO, f"Done! {nodes_read} nodes read.")
    print(
        f"Dispatching {max_cores} workers. This will take a while, so go outside and do something!"
    )
    logger.log(
        logging.INFO,
        f"Dispatching {max_cores} workers. This will take a while, so go outside and do something!",
    )

    # Prepare and dispatch worker processes
    workers = []
    for i in range(max_cores):
        worker = Worker(
            nodes_to_calc, calculated_tuples, nodes_read, df_edges, log_queue
        )
        workers.append(worker)
        worker.start()

    # Write to output file as the workers process the nodes
    with open(f"{csv_output}", "w") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "fp_int_id",
                "fp_cluster_id",
                "cp_level",
                "num_cited_references",
                "num_citing_edges_from_same_cluster",
                "num_citing_nodes_from_same_cluster",
                "num_cited_nodes_from_same_cluster",
                "tr_citing_both_from_same_cluster",
                "tr_cited_both_from_same_cluster",
                "cp_citing_nonzero_citing_from_same_cluster",
                "cp_cited_nonzero_from_same_cluster",
            ],
        )
        writer.writeheader()
        while nodes_calculated != nodes_read:
            tup = calculated_tuples.get()
            writer.writerow(
                {
                    "fp_int_id": tup[0],
                    "fp_cluster_id": tup[1],
                    "cp_level": tup[2],
                    "num_cited_references": tup[3],
                    "num_citing_edges_from_same_cluster": tup[4],
                    "num_citing_nodes_from_same_cluster": tup[5],
                    "num_cited_nodes_from_same_cluster": tup[6],
                    "tr_citing_both_from_same_cluster": tup[7],
                    "tr_cited_both_from_same_cluster": tup[8],
                    "cp_citing_nonzero_citing_from_same_cluster": tup[9],
                    "cp_cited_nonzero_from_same_cluster": tup[10],
                }
            )
            nodes_calculated += 1

    # Wait for workers to finish before closing the logger and exiting
    for w in workers:
        w_pid = w.pid
        w.join()
        print(f"Closing process {w_pid}")
        logger.log(logging.INFO, f"Closing child process {w_pid}")

    run_time = time.time() - start_time
    print(f"Finished calculating BDID for {nodes_read} nodes in {run_time} seconds")
    logger.log(
        logging.INFO,
        f"Finished calculating BDID for {nodes_read} nodes in {run_time} seconds",
    )

    print(f"Sampling complete. Output written at: \n\t{csv_output}")
    logger.log(logging.INFO, f"Sampling complete. Output written at: {csv_output}")

    run_time = time.time() - start_time
    print(f"Finished operating on {nodes_read} nodes in {run_time} seconds")
    logger.log(
        logging.INFO, f"Finished operating on {nodes_read} nodes in {run_time} seconds"
    )
    # Signal to the logger that we're done
    log_queue.put_nowait(None)
    log_queue.close()
    log_listener.join()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Too many arguments. See usage below:")
        print("Usage: collect_clustered.py [num_cores]")
        print("\tArguments:")
        print(
            "\t\tnum_cores: Optional. Maximum number of CPU cores to use. Defaults to 8."
        )
        exit(1)
    main(int(sys.argv[1]))
