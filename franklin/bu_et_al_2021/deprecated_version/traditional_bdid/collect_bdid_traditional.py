# Utility Imports
import csv
from datetime import datetime
import os
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
        df: pd.DataFrame,
        log_queue: Queue,
    ):
        super().__init__(daemon=True)
        self.nodes_to_calc = nodes_to_calc
        self.calculated_tuples = calculated_tuples
        self.nodes_read = nodes_read
        self.df = df
        self.log_queue = log_queue

    def run(self):
        logger = logging.getLogger("Logger")

        while True:

            next_node = self.nodes_to_calc.get()

            if next_node is None:
                self.nodes_to_calc.put_nowait(None)
                self.nodes_to_calc.close()
                self.calculated_tuples.put(None)
                print(f"Process {current_process().pid} is ready to join.")
                break

            focal_int_id = next_node

            print(
                f"Process {current_process().pid} has started pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue)"
            )
            # logger.log(
            #     logging.INFO,
            #     f"Process {current_process().pid} has started pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue)",
            # )

            # Get all edges where the cited_int_id is the focal
            focal_incoming_edges = self.df.loc[
                (self.df["cited_int_id"] == focal_int_id)
            ]

            cp_level = len(focal_incoming_edges.index)

            # If the cp_level is 0, then everything is zero
            if cp_level == 0:
                tup = (
                    focal_int_id,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                )
                self.calculated_tuples.put(tup)
                print(f"cp_level = 0 for pub {focal_int_id}")
                # logger.log(logging.INFO, f"cp_level = 0 for pub {focal_int_id}")
                print(
                    f"Process {current_process().pid} has finished pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue)"
                )
                if self.nodes_to_calc.qsize() % 1000 == 0:
                    logger.log(
                        logging.INFO,
                        f"{self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue.",
                    )
                # logger.log(
                #     logging.INFO,
                #     f"Process {current_process().pid} has finished pub {focal_int_id} ({self.calculated_tuples.qsize()} / {self.nodes_read} finished",
                # )
                continue

            # Get the edges where the citing_int_id also cites
            # another pub that cites focal_int_id
            bread_depth_df = self.df.loc[
                (
                    self.df["citing_int_id"].isin(focal_incoming_edges["citing_int_id"])
                    & self.df["cited_int_id"].isin(
                        focal_incoming_edges["citing_int_id"]
                    )
                )
            ]

            # Get focal_pub's outgoing edges
            focal_outgoing_edges = self.df.loc[
                (self.df["citing_int_id"] == focal_int_id)
            ]

            # Get the edges where the citing_int_id also cites the
            # pubs that focal_pub cites
            ind_dep_df = self.df.loc[
                (
                    self.df["citing_int_id"].isin(focal_incoming_edges["citing_int_id"])
                    & self.df["cited_int_id"].isin(focal_outgoing_edges["cited_int_id"])
                )
            ]

            # TR[citing] and TR[cited] are natively tracked in these dataframes
            tr_citing = len(bread_depth_df.index)
            tr_cited = len(ind_dep_df.index)

            # Get the number of unique citing_ids for each dataframe
            unique_citing_ids_bread_depth = bread_depth_df.drop_duplicates(
                subset=["citing_int_id"]
            )
            unique_citing_ids_ind_dep = ind_dep_df.drop_duplicates(
                subset=["citing_int_id"]
            )

            cp_r_citing_nonzero = len(unique_citing_ids_bread_depth.index)
            cp_r_cited_nonzero = len(unique_citing_ids_ind_dep.index)

            # cp_level = cp_r_cit[ing/ed]_zero + cp_r_cit[ing/ed]_nonzero
            cp_r_citing_zero = cp_level - cp_r_citing_nonzero
            cp_r_cited_zero = cp_level - cp_r_cited_nonzero

            pcp_r_citing_zero = cp_r_citing_zero / cp_level
            pcp_r_citing_nonzero = cp_r_citing_nonzero / cp_level
            pcp_r_cited_zero = cp_r_cited_zero / cp_level
            pcp_r_cited_nonzero = cp_r_cited_nonzero / cp_level
            mr_citing = tr_citing / cp_level
            mr_cited = tr_cited / cp_level

            # Place into synchronous queue for the main process
            tup = (
                focal_int_id,
                cp_level,
                cp_r_citing_zero,
                cp_r_citing_nonzero,
                tr_citing,
                pcp_r_citing_zero,
                pcp_r_citing_nonzero,
                mr_citing,
                cp_r_cited_zero,
                cp_r_cited_nonzero,
                tr_cited,
                pcp_r_cited_zero,
                pcp_r_cited_nonzero,
                mr_cited,
            )
            self.calculated_tuples.put(tup)
            print(
                f"Process {current_process().pid} has finished pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue)"
            )
            if self.nodes_to_calc.qsize() % 1000 == 0:
                logger.log(
                    logging.INFO,
                    f"{self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue",
                )
            # logger.log(
            #     logging.INFO,
            #     f"Process {current_process().pid} has finished pub {focal_int_id} ({self.calculated_tuples.qsize()} / {self.nodes_read} finished",
            # )


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


def main(path_to_edge_list: str, max_cores: int = 8):

    if max_cores > 64:
        max_cores = 64
    
    # Reduce to account for the logger process
    max_cores -= 1

    # Format names of output files
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    start_time = time.time()
    csv_output = f"fmoy3_bdid_metrics-{exec_time}.csv"
    logfile_output = f"logfile_collect_bdid_data_{exec_time}.txt"

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

    print("Generating dataframe. This will take a minute...")
    logger.log(logging.INFO, "Generating dataframe. This will take a minute...")

    # Create a copy of the edge list into a Pandas Dataframe
    df = pd.read_csv(
        path_to_edge_list,
        sep="\t",
        names=["citing_int_id", "cited_int_id"],
    )

    print(df)
    logger.log(logging.INFO, f"\n{df}")
    print("Done!")
    logger.log(logging.INFO, "Done!")
    print("Reading node list...")
    logger.log(logging.INFO, "Reading node list")

    # Read in the node list (currently using the sample)
    node_list = set()
    nodes_to_calc = Queue()
    manager = Manager()
    # Must use a manager-based queue to handle more than 64 child processes
    calculated_tuples = manager.Queue()
    with open(
        path_to_edge_list,
        "r",
    ) as file:
        reader = csv.DictReader(file, fieldnames=["citing_int_id", "cited_int_id"], delimiter='\t')
        for row in reader:
            if int(row["citing_int_id"]) not in node_list:
                node_list.add(int(row["citing_int_id"]))
                nodes_to_calc.put(int(row["citing_int_id"]))
            if int(row["cited_int_id"]) not in node_list:
                node_list.add(int(row["cited_int_id"]))
                nodes_to_calc.put(int(row["cited_int_id"]))

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
        worker = Worker(nodes_to_calc, calculated_tuples, nodes_read, df, log_queue)
        workers.append(worker)
        worker.start()

    # Write computed items to output as the workers are working
    # TODO: Turn this into a CSVWriter module like in the clustered version
    with open(f"{csv_output}", "w") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "pub_int_id",
                "cp_level",
                "cp_r_citing_zero",
                "cp_r_citing_nonzero",
                "tr_citing",
                "pcp_r_citing_zero",
                "pcp_r_citing_nonzero",
                "mr_citing",
                "cp_r_cited_zero",
                "cp_r_cited_nonzero",
                "tr_cited",
                "pcp_r_cited_zero",
                "pcp_r_cited_nonzero",
                "mr_cited",
            ],
        )
        writer.writeheader()
        while True:
            tup = calculated_tuples.get()
            if tup is None:
                # Should only proceed to join children when they have all put Nones in
                if calculated_tuples.qsize() == 0:
                    break
                else:
                    continue
            writer.writerow(
                {
                    "pub_int_id": tup[0],
                    "cp_level": tup[1],
                    "cp_r_citing_zero": tup[2],
                    "cp_r_citing_nonzero": tup[3],
                    "tr_citing": tup[4],
                    "pcp_r_citing_zero": tup[5],
                    "pcp_r_citing_nonzero": tup[6],
                    "mr_citing": tup[7],
                    "cp_r_cited_zero": tup[8],
                    "cp_r_cited_nonzero": tup[9],
                    "tr_cited": tup[10],
                    "pcp_r_cited_zero": tup[11],
                    "pcp_r_cited_nonzero": tup[12],
                    "mr_cited": tup[13],
                }
            )
    
    # Close worker processes
    for w in workers:
        w_pid = w.pid
        w.join()
        print(f"Closing process {w_pid}")
        logger.log(logging.INFO, f"Closing child process {w_pid}")

    print(f"Sampling complete. Writing to output: \n\t{csv_output}")
    logger.log(logging.INFO, f"Sampling complete. Writing to output: {csv_output}")

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
    if len(sys.argv) != 2 or len(sys.argv) != 3:
        print("Invalid number of arguments. See usage below:")
        print("Usage: collect_bdid_traditional.py path_to_edge_list [num_workers]")
        print("\tArguments:")
        print(
            "\t\tpath_to_edge_list: Path to the TSV containing the list of edges."
        )
        print(
            "\t\tnum_cores: Optional. Maximum number of CPU cores to use. Defaults to 8."
        )
        exit(1)

    # Check validity of input path
    if os.path.exists(sys.argv[1]) == False:
        print("The specified path_to_edge_list could not be found. Please check the file name and try again.")
        exit(1)

    main(sys.argv[1], int(sys.argv[2]))
