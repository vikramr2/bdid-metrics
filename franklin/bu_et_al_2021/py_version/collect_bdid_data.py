# Utility Imports
import csv
from datetime import datetime
import sys
import time

import pandas as pd

from multiprocessing import Process, Queue, current_process

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
                break

            focal_int_id = next_node[0]
            cluster_id = next_node[1]

            print(
                f"Process {current_process().pid} has started pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs queued)"
            )
            logger.log(
                logging.INFO,
                f"Process {current_process().pid} has started pub {focal_int_id} ({self.nodes_to_calc.qsize()} / {self.nodes_read} pubs queued)",
            )

            # Prepare calcs
            cp_r_citing_zero = 0
            cp_r_citing_nonzero = 0
            cp_r_cited_zero = 0
            cp_r_cited_nonzero = 0
            tr_citing = 0
            tr_cited = 0

            # Get all edges where the cited_int_id is the focal
            focal_incoming_edges = self.df.loc[
                (self.df["cited_int_id"] == focal_int_id)
            ]

            cp_level = len(focal_incoming_edges.index)

            for row in focal_incoming_edges.itertuples(index=False):
                # Count r_citing by going through all citing int ids and getting
                # the number of edges where the current citing_int_id cites a pub
                # that also cites focal_int_id
                r_citing_subquery = self.df.loc[
                    (self.df["cited_int_id"] == focal_int_id)
                    & (self.df["citing_int_id"] != getattr(row, "citing_int_id"))
                ]

                r_citing_major_query = self.df.loc[
                    (self.df["citing_int_id"] == getattr(row, "citing_int_id"))
                    & (self.df["cited_int_id"].isin(r_citing_subquery["citing_int_id"]))
                ]
                r_citing = len(r_citing_major_query.index)

                # Count r_citing by going through all the citing int ids and getting
                # the number of edges where the current citing_int_id cites a pub
                # that focal_int_id also cites
                r_cited_subquery = self.df.loc[
                    (self.df["citing_int_id"] == focal_int_id)
                ]
                r_cited_major_query = self.df.loc[
                    (self.df["citing_int_id"] == getattr(row, "citing_int_id"))
                    & (self.df["cited_int_id"].isin(r_cited_subquery["cited_int_id"]))
                ]
                r_cited = len(r_cited_major_query.index)

                # Accumulate TR[citing] and TR[cited]
                tr_citing += r_citing
                tr_cited += r_cited

                # Increment corresponding CP counters
                if r_citing == 0:
                    cp_r_citing_zero += 1
                elif r_citing > 0:
                    cp_r_citing_nonzero += 1
                else:
                    print("r_citing has an invalid value")

                if r_cited == 0:
                    cp_r_cited_zero += 1
                elif r_cited > 0:
                    cp_r_cited_nonzero += 1
                else:
                    print("r_cited has an invalid value")
                # END LOOP

            # Calculate proportions
            if cp_level == 0:
                print(f"cp_level = 0 for pub {focal_int_id}")
                logger.log(logging.INFO, f"cp_level = 0 for pub {focal_int_id}")
                pcp_r_citing_zero = 0
                pcp_r_citing_nonzero = 0
                pcp_r_cited_zero = 0
                pcp_r_cited_nonzero = 0
                mr_citing = 0
                mr_cited = 0
            else:
                pcp_r_citing_zero = cp_r_citing_zero / cp_level
                pcp_r_citing_nonzero = cp_r_citing_nonzero / cp_level
                pcp_r_cited_zero = cp_r_cited_zero / cp_level
                pcp_r_cited_nonzero = cp_r_cited_nonzero / cp_level
                mr_citing = tr_citing / cp_level
                mr_cited = tr_cited / cp_level

            # Place into synchronous queue for the main process
            tup = (
                focal_int_id,
                cluster_id,
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
                f"Process {current_process().pid} has finished pub {focal_int_id} ({self.calculated_tuples.qsize()} / {self.nodes_read} finished)"
            )
            logger.log(
                logging.INFO,
                f"Process {current_process().pid} has finished pub {focal_int_id} ({self.calculated_tuples.qsize()} / {self.nodes_read} finished",
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
        "/srv/local/shared/external/for_eleanor/gc_exosome/citing_cited_network.integer.tsv",
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
    nodes_to_calc = Queue()
    calculated_tuples = Queue()
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
        worker = Worker(nodes_to_calc, calculated_tuples, nodes_read, df, log_queue)
        workers.append(worker)
        worker.start()

    # Wait for workers to finish before writing calculated_tuples to CSV
    for w in workers:
        w.join()

    print("Sampling complete. Writing to output...")
    logger.log(logging.INFO, "Sampling complete. Writing to output...")

    with open(f"{csv_output}", "w") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "pub_int_id",
                "cluster_id",
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
        while not calculated_tuples.empty():
            tup = calculated_tuples.get()
            writer.writerow(
                {
                    "pub_int_id": tup[0],
                    "cluster_id": tup[1],
                    "cp_level": tup[2],
                    "cp_r_citing_zero": tup[3],
                    "cp_r_citing_nonzero": tup[4],
                    "tr_citing": tup[5],
                    "pcp_r_citing_zero": tup[6],
                    "pcp_r_citing_nonzero": tup[7],
                    "mr_citing": tup[8],
                    "cp_r_cited_zero": tup[9],
                    "cp_r_cited_nonzero": tup[10],
                    "tr_cited": tup[11],
                    "pcp_r_cited_zero": tup[12],
                    "pcp_r_cited_nonzero": tup[13],
                    "mr_cited": tup[14],
                }
            )

    run_time = time.time() - start_time
    print(f"Finished operating on {nodes_read} nodes in {run_time} seconds")
    logger.log(
        logging.INFO, f"Finished operating on {nodes_read} nodes in {run_time} seconds"
    )
    # Signal to the logger that we're done
    log_queue.put_nowait(None)
    log_listener.join()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Too many arguments. See usage below:")
        print("Usage: collect_bdid_data.py [num_cores]")
        print("\tArguments:")
        print(
            "\t\tnum_cores: Optional. Maximum number of CPU cores to use. Defaults to 8."
        )
        exit(1)
    main(int(sys.argv[1]))
