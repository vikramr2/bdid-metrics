# Process Leiden output on snap/orkut in stages
# preparatory to running CM
# 12/26/2023

import belinda as bl
import polars as pl
import os

os.chdir('/data1/snap_leiden_venv/cit_hepph/')
g = bl.Graph("./cit_hepph_cleaned.tsv")

c5 = bl.read_membership(g,"cit_hepph_leiden.5.tsv")
c1 = bl.read_membership(g,"cit_hepph_leiden.1.tsv")
c01 = bl.read_membership(g,"cit_hepph_leiden.01.tsv")
c001 = bl.read_membership(g,"cit_hepph_leiden.001.tsv")

#remove trees
c5_wt = c5.filter(pl.col('n') != pl.col('m') + 1)
c1_wt = c1.filter(pl.col('n') != pl.col('m') + 1)
c01_wt = c01.filter(pl.col('n') != pl.col('m') + 1)
c001_wt = c001.filter(pl.col('n') != pl.col('m') + 1)

bl.write_membership(g, c5_wt, "cit_hepph_leiden.5_nontree_clusters.tsv")
bl.write_membership(g, c1_wt, "cit_hepph_leiden.1_nontree_clusters.tsv")
bl.write_membership(g, c01_wt, "cit_hepph_leiden.01_nontree_clusters.tsv")
bl.write_membership(g, c001_wt, "cit_hepph_leiden.001_nontree_clusters.tsv")

# filter N > 10
c5_wt_n10 = c5_wt.filter(pl.col('n') > 10) 
c1_wt_n10 = c1_wt.filter(pl.col('n') > 10) 
c01_wt_n10 = c01_wt.filter(pl.col('n') > 10) 
c001_wt_n10 = c001_wt.filter(pl.col('n') > 10)

bl.write_membership(g, c5_wt_n10, "cit_hepph_leiden.5_nontree_n10_clusters.tsv")
bl.write_membership(g, c1_wt_n10, "cit_hepph_leiden.1_nontree_n10_clusters.tsv")
bl.write_membership(g, c01_wt_n10, "cit_hepph_leiden.01_nontree_n10_clusters.tsv")
bl.write_membership(g, c001_wt_n10, "cit_hepph_leiden.001_nontree_n10_clusters.tsv")






