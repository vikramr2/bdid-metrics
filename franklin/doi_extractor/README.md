# DOI Extractor
## About
This folder contains two scripts that can be used to extract DOIs from a PDF file. It uses `pdftotext` to convert the input PDF file to text, collects DOIs using regex matching, and outputs its findings to a file.

There are two versions of the script:
- `doi_extractor.py` is a simple version of the script. This version preserves the line structure of the pdftotext conversion. Because of the nature of the regex used, this version of the script cannot collect some DOIs which are broken into multiple lines.
- `doi_extractor_aggressive.py` is a more aggressive version of the script. This version eliminates all newlines and is guaranteed to find all DOIs. Unfortunately, a side effect of eliminating newlines is the possibility that extra characters get added to DOIs that don't end in a semicolon. 

## Dependencies
- Python 3.7+
- pdftotext (already installed on EWS, installable from package manager)

## Usage
**Simple version**: `python3 doi_extractor.py input_pdf`\
**Aggressive version**: `python3 doi_extractor_aggressive.py input_pdf`\
**Argument**: `input_pdf` is the path to the pdf file