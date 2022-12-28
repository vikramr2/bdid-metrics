# Process cm output and refilter for trees
# Assigned abbreviation: lfrwtp.5

import belinda as bl
import polars as pl
import os
import glob

os.chdir('/data1/snap_leiden_venv/cit_hepph/')
input_path_files=os.path.join(os.getcwd(), "*.out.tsv.after.json")
files=list(glob.glob(input_path_files))
files.sort()
print(files)

g = bl.Graph("./cit_hepph_cleaned.tsv")

# read in output from the first round of cm-cm_universal
r2c001 = bl.read_json(g,files[0])
r2c01 = bl.read_json(g,files[1])
r2c1 = bl.read_json(g,files[2])
r2c5 = bl.read_json(g,files[3])

#remove trees
r2c5_wt = r2c5.filter(pl.col('n') != pl.col('m') + 1)
r2c1_wt = r2c1.filter(pl.col('n') != pl.col('m') + 1)
r2c01_wt = r2c01.filter(pl.col('n') != pl.col('m') + 1)
r2c001_wt = r2c001.filter(pl.col('n') != pl.col('m') + 1)

bl.write_membership(g, r2c5_wt, "cit_hepph_leiden.5_r2nontree_clusters.tsv")
bl.write_membership(g, r2c1_wt, "cit_hepph_leiden.1_r2nontree_clusters.tsv")
bl.write_membership(g, r2c01_wt, "cit_hepph_leiden.01_r2nontree_clusters.tsv")
bl.write_membership(g, r2c001_wt, "cit_hepph_leiden.001_r2nontree_clusters.tsv")

# filter N > 10

r2c5_wt_n10 = r2c5_wt.filter(pl.col('n') > 10)
r2c1_wt_n10 = r2c1_wt.filter(pl.col('n') > 10)
r2c01_wt_n10 = r2c01_wt.filter(pl.col('n') > 10)
r2c001_wt_n10 = r2c001_wt.filter(pl.col('n') > 10) 

bl.write_membership(g, r2c5_wt_n10, "cit_hepph_leiden.5_r2nontree_n10_clusters.tsv")
bl.write_membership(g, r2c1_wt_n10, "cit_hepph_leiden.1_r2nontree_n10_clusters.tsv")
bl.write_membership(g, r2c01_wt_n10, "cit_hepph_leiden.01_r2nontree_n10_clusters.tsv")
bl.write_membership(g, r2c001_wt_n10, "cit_hepph_leiden.001_r2nontree_n10_clusters.tsv")










