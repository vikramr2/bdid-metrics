import os
import pandas as pd
import sys


def main(csv_one_path: str, csv_two_path: str):
    print("Generating Pandas dataframes...")

    # Read CSVs
    # left_df = pd.read_csv('/srv/local/shared/external/dbid/bu_all.csv')
    # right_df = pd.read_csv('/home/fmoy3/git_repo/franklin/bu_et_al_2021/py_version/fmoy3_bdid_metrics-2022-02-14-07-44-42.csv')
    left_df = pd.read_csv(csv_one_path)
    right_df = pd.read_csv(csv_two_path)

    # Drop extraneous columns
    # right_df.drop(
    #     [
    #         "cluster_id",
    #         "pcp_r_citing_zero_clustered",
    #         "pcp_r_citing_nonzero_clustered",
    #         "mr_citing_clustered",
    #         "pcp_r_cited_zero_clustered",
    #         "pcp_r_cited_nonzero_clustered",
    #         "mr_cited_clustered",
    #     ],
    #     axis=1,
    #     inplace=True,
    # )

    # Reorder to match George's col names
    right_df.rename(
        columns={
            "fp_int_id": "fp",
            "cp_r_citing_zero": "cp_r_citing_pub_zero",
            "cp_r_citing_nonzero": "cp_r_citing_pub_nonzero",
            "tr_cited": "tr_cited_pub",
            "cp_r_cited_nonzero": "cp_r_cited_pub_nonzero",
            "cp_r_cited_zero": "cp_r_cited_pub_zero",
        },
        inplace=True,
    )
    right_df = right_df[
        [
            "fp",
            "cp_level",
            "cp_r_citing_pub_nonzero",
            "cp_r_citing_pub_zero",
            "tr_citing",
            "tr_cited_pub",
            "cp_r_cited_pub_nonzero",
            "cp_r_cited_pub_zero",
        ]
    ]

    # For some reason, George's original DF had nulls
    # print(left_df['fp'].isnull()[left_df['fp'].isnull() == True])
    # left_df.dropna(inplace=True)
    # left_df["fp"] = left_df["fp"].astype(int)

    # Filter to match dataset
    left_df_subset = left_df[(left_df["fp"].isin(right_df["fp"]))]
    right_df_subset = right_df[(right_df["fp"].isin(left_df_subset["fp"]))]

    # Sort both subsets and drop their indices as we only want to check raw data
    right_df_subset = right_df_subset.sort_values("fp").reset_index(drop=True)
    left_df_subset = left_df_subset.sort_values("fp").reset_index(drop=True)

    # Print results
    print("\nLeft CSV's data:")
    print(left_df_subset)
    print("\nRight CSV's data:")
    print(right_df_subset)
    print(f"\nAre equal: {right_df_subset.equals(left_df_subset)}")


if __name__ == "__main__":
    # Verify existence of both files
    if os.path.exists(sys.argv[1]) == False:
        print(
            f"Could not find {sys.argv[1]}. Please check the file name and try again."
        )
        exit(1)
    if os.path.exists(sys.argv[2]) == False:
        print(
            f"Could not find {sys.argv[2]}. Please check the file name and try again."
        )
        exit(1)

    main(sys.argv[1], sys.argv[2])