# Utility Imports
import csv
from datetime import datetime
import os
import sys
import time

import pandas as pd

from multiprocessing import Manager, Queue

import logging
import logging.handlers

# Custom class imports
from csv_writer import CsvWriter
from log_listener import LogListener
from worker import Worker


def main(path_to_clustering_file: str, path_to_edge_list: str, max_cores: int = 8):

    # Full-scale is memory intensive, so don't launch too many workers
    if max_cores > 32:
        max_cores = 32
    
    # Reduce to account for the logger and writer workers
    max_cores -= 2

    # Format names of output files
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    start_time = time.time()
    csv_output = f"clustered_bdid_metrics-{exec_time}.csv"
    logfile_output = f"logfile_collect_clustered_{exec_time}.txt"

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
    print(
        f"Using {max_cores} workers ({max_cores+2} including logger and csv_writer)..."
    )
    logger.log(
        logging.INFO,
        f"Using {max_cores} workers ({max_cores+2} including logger and csv_writer)...",
    )

    print("Generating dataframe. This will take a minute...")
    logger.log(logging.INFO, "Generating dataframe. This will take a minute...")

    # Put edge list into a dataframe
    df_edges = pd.read_csv(
        path_to_edge_list,
        sep="\t",
        names=["citing_int_id", "cited_int_id"],
    )

    # Put edge list with each endpoint's cluster_id into a dataframe
    # Note that some edges will be lost if either or both of its
    # endpoints were part of kmp-invalid clusters
    df_edges_clustered = pd.read_csv(
        path_to_edge_list,
        sep="\t",
        names=["citing_int_id", "cited_int_id"],
    )
    df_clusters = pd.read_csv(
        path_to_clustering_file,
        names=["citing_int_id", "citing_cluster_id"],
    )
    df_edges_clustered = df_edges_clustered.merge(
        df_clusters, on="citing_int_id", how="inner"
    )
    df_clusters = pd.read_csv(
        path_to_clustering_file,
        names=["cited_int_id", "cited_cluster_id"],
    )
    df_edges_clustered = df_edges_clustered.merge(
        df_clusters, on="cited_int_id", how="inner"
    )

    print(df_edges)
    logger.log(logging.INFO, f"\n{df_edges}")
    print("Done!")
    logger.log(logging.INFO, "Done!")
    print("Reading node list...")
    logger.log(logging.INFO, "Reading node list")

    # Read in the node list (currently using the sample)
    nodes_to_calc = Queue()
    manager = Manager()
    # Must use a manager-based queue to handle more than 64 child processes
    calculated_tuples = manager.Queue()
    # Full-scale: "/srv/local/shared/external/clusterings/exosome_1900_2010_sabpq/IKC+RG+Aug+kmp-parse/ikc-rg-aug_k_5_p_2.clustering"
    # Sample: "/srv/local/shared/external/dbid/franklins_sample.csv"
    with open(
        path_to_clustering_file,
        "r",
    ) as file:
        reader = csv.DictReader(file, fieldnames=["V1", "V2"])
        # reader = csv.DictReader(file)
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
    for _ in range(max_cores):
        worker = Worker(
            nodes_to_calc,
            calculated_tuples,
            nodes_read,
            df_edges,
            df_edges_clustered,
            log_queue,
        )
        workers.append(worker)
        worker.start()

    # Start csv_writer
    csv_writer = CsvWriter(csv_output, calculated_tuples)
    csv_writer.start()

    # Wait for workers to finish and join
    for w in workers:
        w_pid = w.pid
        w.join()
        print(f"Closing process {w_pid}")
        logger.log(logging.INFO, f"Closing child process {w_pid}")

    # Tell the csv_writer process that the workers have finished
    calculated_tuples.put(None)
    csv_writer.join()
    print("Closing CsvWriter process")
    logger.log(logging.INFO, "Closing CsvWriter process")

    run_time = time.time() - start_time
    print(f"Finished calculating BDID for {nodes_read} nodes in {run_time} seconds")
    logger.log(
        logging.INFO,
        f"Finished calculating BDID for {nodes_read} nodes in {run_time} seconds",
    )
    # Signal to the logger that we're done
    log_queue.put_nowait(None)
    log_queue.close()
    log_listener.join()


if __name__ == "__main__":
    if len(sys.argv) != 3 or len(sys.argv) != 4:
        print("Invalid number of arguments. See usage below:")
        print(
            "Usage: collect_clustered_full.py path_to_clustering_file path_to_edge_list [num_workers]"
        )
        print("\tArguments:")
        print(
            "\t\tpath_to_clustering_file: Path to the CSV containing clustering info."
        )
        print("\t\path_to_edge_list: Path to the TSV containing the list of edges.")
        print(
            "\t\tnum_workers: Optional. Maximum number of parallel workers to use. Defaults to 8."
        )
        exit(1)

    # Check validity of input paths
    if os.path.exists(sys.argv[1]) == False:
        print(
            "The specified path_to_clustering_file could not be found. Please check the file name and try again."
        )
        exit(1)
    if os.path.exists(sys.argv[2]) == False:
        print(
            "The specified path_to_edge_list could not be found. Please check the file name and try again."
        )
        exit(1)

    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
