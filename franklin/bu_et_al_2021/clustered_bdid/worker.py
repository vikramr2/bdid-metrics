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
        df_edges: pd.DataFrame,
        df_edges_clustered: pd.DataFrame,
        log_queue: Queue,
    ):
        super().__init__(daemon=True)
        self.nodes_to_calc = nodes_to_calc
        self.calculated_tuples = calculated_tuples
        self.nodes_read = nodes_read
        self.df_edges = df_edges
        self.df_edges_clustered = df_edges_clustered
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
            
            # Filter the edge list to edges in the cluster
            intra_cluster_edges = self.df_edges_clustered.loc[
                (
                    (self.df_edges_clustered["citing_cluster_id"] == cluster_id)
                    & (self.df_edges_clustered["cited_cluster_id"] == cluster_id)
                )
            ]

            # Get all intra_cluster edges where the cited_int_id is the focal
            focal_incoming_edges_clustered = intra_cluster_edges.loc[
                (intra_cluster_edges["cited_int_id"] == focal_int_id)
            ]

            cp_level = len(focal_incoming_edges.index)
            cp_level_cluster = len(focal_incoming_edges_clustered.index)

            # If the cp_level is 0, then everything is zero
            if cp_level == 0:
                tup = (
                    focal_int_id,
                    cluster_id,
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
                continue

            # If the cp_level_cluster is 0, then everything is zero except for the level
            if cp_level_cluster == 0:
                tup = (
                    focal_int_id,
                    cluster_id,
                    cp_level,
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
                continue

            # Get the edges where the citing_int_id also cites
            # another pub that cites focal_int_id
            bread_depth_df = intra_cluster_edges.loc[
                (
                    intra_cluster_edges["citing_int_id"].isin(
                        focal_incoming_edges_clustered["citing_int_id"]
                    )
                    & intra_cluster_edges["cited_int_id"].isin(
                        focal_incoming_edges_clustered["citing_int_id"]
                    )
                )
            ]

            # Get focal_pub's outgoing edges
            focal_outgoing_edges = intra_cluster_edges.loc[
                (intra_cluster_edges["citing_int_id"] == focal_int_id)
            ]

            # Get the edges where the citing_int_id also cites the
            # pubs that focal_pub cites
            ind_dep_df = intra_cluster_edges.loc[
                (
                    intra_cluster_edges["citing_int_id"].isin(
                        focal_incoming_edges_clustered["citing_int_id"]
                    )
                    & intra_cluster_edges["cited_int_id"].isin(
                        focal_outgoing_edges["cited_int_id"]
                    )
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
            cp_r_citing_zero = cp_level_cluster - cp_r_citing_nonzero
            cp_r_cited_zero = cp_level_cluster - cp_r_cited_nonzero

            pcp_r_citing_zero = cp_r_citing_zero / cp_level_cluster
            pcp_r_citing_nonzero = cp_r_citing_nonzero / cp_level_cluster
            pcp_r_cited_zero = cp_r_cited_zero / cp_level_cluster
            pcp_r_cited_nonzero = cp_r_cited_nonzero / cp_level_cluster
            mr_citing = tr_citing / cp_level_cluster
            mr_cited = tr_cited / cp_level_cluster

            # Place into synchronous queue for the main process
            tup = (
                focal_int_id,
                cluster_id,
                cp_level,
                cp_level_cluster,
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
                    f"{self.nodes_to_calc.qsize()} / {self.nodes_read} pubs in queue.",
                )
