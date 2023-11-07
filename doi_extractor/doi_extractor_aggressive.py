import os
import re
import subprocess
import sys
from datetime import datetime


def main(arg_list: list):
    """Takes path to a PDF file as an argument, runs pdftotext on it, and then prints the list of found DOIs"""
    usage_statement = "Usage: python3 doi_extractor_agressive.py input_pdf"
    args_statement = "Arguments:\n\tinput_pdf: Path to the PDF file to scrape DOIs from.\
                    \n\tOutputs to doi_list-aggressive-YYYY-mm-dd-HH-MM-SS.txt"

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
    doi_extractor_output = f"doi_list-aggressive-{exec_time}.txt"

    # Call pdftotext and put each line into a list
    subprocess.call(["pdftotext", arg_list[1], pdftotext_output])
    with open(pdftotext_output, "r") as file:
        pdf_as_list = file.readlines()

    # Catch CrossRef DOIs that bleed to new lines by joining and removing newlines
    pdf_as_one_string = "".join(pdf_as_list)
    pdf_as_one_string = pdf_as_one_string.replace("\n", "")
    regex_one = re.compile(r"10.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)

    # Match DOIS that newline immediately after 10.xxxx/
    # regex_two = re.compile(r'10.\d{4,9}\/\n?[-._;()\/:A-Z0-9]+[;\n]', re.IGNORECASE)
    # EDGE CASE: 10.1146/annurev-cancerbio-030617-050519 (Hyphen got corrupted)

    # Match DOIs, strip unnecessary chars, and write to output file
    found_dois = regex_one.findall(pdf_as_one_string)
    with open(doi_extractor_output, "w") as file:
        for doi in found_dois:
            has_semicolon = doi.find(";")
            if has_semicolon != -1:
                doi = doi[0:has_semicolon]
            file.write(doi + "\n")

    print(f"Finished! Output location: {doi_extractor_output}")


if __name__ == "__main__":
    main(sys.argv)
