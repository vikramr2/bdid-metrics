import pandas as pd

def convert_csv_to_tsv(input_csv_file, output_tsv_file):
    # Read the CSV file into a DataFrame, skipping the first line
    df = pd.read_csv(input_csv_file)

    # Write the DataFrame to a TSV file
    df.to_csv(output_tsv_file, sep='\t', index=False)

if __name__ == "__main__":
    # Replace 'input.csv' and 'output.tsv' with your file names
    convert_csv_to_tsv('pi3k_pubmed_restricted_el.csv', 'pi3k_pubmed_restricted_el.tsv')