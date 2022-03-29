from datetime import datetime
import pandas as pd


def main():
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    george_csv = pd.read_csv(
        "/home/fmoy3/git_repo/franklin/bu_et_al_2021/bdid_samples/bu_all.csv"
    )
    clustered_csv = pd.read_csv(
        "/home/fmoy3/git_repo/franklin/clustered_bdid_metrics-2022-03-24-14-46-01.csv"
    )
    clustered_csv.rename(
        columns={"fp_int_id": "fp", "cp_level": "c.cp_level"}, inplace=True
    )

    # Join the two CSVs
    joined_csv = george_csv.merge(clustered_csv, how="inner", on="fp")
    joined_csv.drop(
        [
            "cluster_id",
            "pcp_r_citing_zero_clustered",
            "pcp_r_citing_nonzero_clustered",
            "mr_citing_clustered",
            "pcp_r_cited_zero_clustered",
            "pcp_r_cited_nonzero_clustered",
            "mr_cited_clustered",
            "c.cp_level",
        ],
        inplace=True,
        axis=1,
    )
    joined_csv.to_csv(
        "/home/fmoy3/git_repo/franklin/bu_et_al_2021/bdid_samples/bu_10_column.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
