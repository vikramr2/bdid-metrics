import csv
from multiprocessing import Process, Queue

class CsvWriter(Process):
    def __init__(self, csv_output: str, calculated_tuples: Queue):
        super().__init__(daemon=True)
        self.csv_output = csv_output
        self.calculated_tuples = calculated_tuples

    def run(self):
        # Write computed items to output as the workers are working
        with open(self.csv_output, "w") as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=[
                    "fp_int_id",
                    "cluster_id",
                    "cp_level",
                    "cp_level_cluster",
                    "cp_r_citing_zero_clustered",
                    "cp_r_citing_nonzero_clustered",
                    "tr_citing_clustered",
                    "pcp_r_citing_zero_clustered",
                    "pcp_r_citing_nonzero_clustered",
                    "mr_citing_clustered",
                    "cp_r_cited_zero_clustered",
                    "cp_r_cited_nonzero_clustered",
                    "tr_cited_clustered",
                    "pcp_r_cited_zero_clustered",
                    "pcp_r_cited_nonzero_clustered",
                    "mr_cited_clustered",
                ],
            )
            writer.writeheader()
            while True:
                tup = self.calculated_tuples.get()
                if tup is None:
                    # When the main process signals completion, terminate
                    break
                writer.writerow(
                    {
                        "fp_int_id": tup[0],
                        "cluster_id": tup[1],
                        "cp_level": tup[2],
                        "cp_level_cluster": tup[3],
                        "cp_r_citing_zero_clustered": tup[4],
                        "cp_r_citing_nonzero_clustered": tup[5],
                        "tr_citing_clustered": tup[6],
                        "pcp_r_citing_zero_clustered": tup[7],
                        "pcp_r_citing_nonzero_clustered": tup[8],
                        "mr_citing_clustered": tup[9],
                        "cp_r_cited_zero_clustered": tup[10],
                        "cp_r_cited_nonzero_clustered": tup[11],
                        "tr_cited_clustered": tup[12],
                        "pcp_r_cited_zero_clustered": tup[13],
                        "pcp_r_cited_nonzero_clustered": tup[14],
                        "mr_cited_clustered": tup[15],
                    }
                )