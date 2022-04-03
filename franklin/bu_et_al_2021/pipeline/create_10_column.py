from datetime import datetime
import os
import pandas as pd
import sys

def main(csv_one: str, csv_two: str, timestamp: str):
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if timestamp == "":
        output_csv = f"bu_10_column-{exec_time}.csv"
    else:
        output_csv = f"bu_10_column-{timestamp}.csv"
    print("Reading CSVs into Pandas...")
    left_csv = pd.read_csv(csv_one)
    right_csv = pd.read_csv(csv_two)
    joined_csv = right_csv.merge(left_csv, how="inner", on="fp_int_id")
    joined_csv.to_csv(output_csv, index=False)
    print(f"Bu 10 Column saved to {output_csv}")


if __name__ == "__main__":    
    
    # Check argument count
    num_args = len(sys.argv)
    if num_args != 3 and num_args != 4:
        print("Invalid number of arguments. See usage below:")
        print("Usage: create_10_column.py csv_one csv_two [timestamp]")
        print("\tArguments:")
        print("\t\tcsv_one: Path to the left CSV to merge to create the 10 column CSV.")
        print("\t\tcsv_two: Path to the right CSV to merge to create the 10 column CSV.")
        print("\t\ttimestamp: Optional. Specifies the timestamp suffix for the output file.")
        print("\t\t\tDefaults to the timestamp of this script's execution.")
        exit(1)
    
    # Check if files exist
    if os.path.exists(sys.argv[1]) == False:
        print(f"Could not find {sys.argv[1]}. Please check the file name and try again.")
        exit(1)

    if os.path.exists(sys.argv[2]) == False:
        print(f"Could not find {sys.argv[2]}. Please check the file name and try again.")
        exit(1)

    # Use the timestamp if provided, otherwise signal to main to generate one
    if num_args == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2], "")
