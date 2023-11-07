import os
import re
import subprocess
import sys
from datetime import datetime


def main(arg_list: list):
    """Takes path to a PDF file as an argument, runs pdftotext on it, and then prints the list of found DOIs"""
    usage_statement = "Usage: python3 doi_extractor.py input_pdf"
    args_statement = "Arguments:\n\tinput_pdf: Path to the PDF file to scrape DOIs from.\
                    \n\tOutputs to doi_list-YYYY-mm-dd-HH-MM-SS.txt"

    # Exit if the script was called with wrong number of parameters
    if len(arg_list) != 2:
        print("Please supply a PDF to search in")
        print(usage_statement)
        print(args_statement)
        os._exit(0)

    # Ensure the input argument is actually a PDF that exists
    file_type_index = arg_list[1].find(".pdf")

    if file_type_index == -1 or not os.path.exists(arg_list[1]):
        print("The specified file is not a PDF or does not exist.")
        os._exit(0)

    # Format names of output files
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    pdftotext_output = f"pdftotext-{exec_time}.txt"
    doi_extractor_output = f"doi_list-{exec_time}.txt"

    # Call pdftotext and put each line into a list (readlines includes \n)
    subprocess.call(["pdftotext", arg_list[1], pdftotext_output])
    with open(pdftotext_output, "r") as file:
        pdf_as_list = file.readlines()

    # Catch CrossRef DOIs that bleed to new lines after the initial slash
    regex_one = re.compile(r"10.\d{4,9}/\n?[-._;()/:A-Z0-9]+", re.IGNORECASE)
    found_dois = []

    # An alternative method to the for loop below is to join pdf_as_list 
    # to a string, modify the regex to account for newlines during and
    # after the DOI, and do a regex findall

    # Iteratively add DOIs
    for line in pdf_as_list:
        match = regex_one.search(line)
        if match != None:
            found_dois.append(match.group())

    # Strip unnecessary chars and write to output file
    with open(doi_extractor_output, "w") as file:
        for doi in found_dois:
            has_semicolon = doi.find(";")
            if has_semicolon != -1:
                doi = doi[0:has_semicolon]
            file.write(doi + "\n")

    print(f"Finished! Output location: {doi_extractor_output}")


if __name__ == "__main__":
    main(sys.argv)
