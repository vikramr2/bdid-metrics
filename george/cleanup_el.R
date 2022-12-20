# script to remove duplicate rows, parallel edges, and self-loops from
# an edge list that is read in using fread into a dataframe
# usage Rscript cleanup_el.R <input filename> <optional_outputfilename>
# output defaults to default.csv
# Input format should be two columns csv, tscv, or whitespace separated
# George Chacko 12/20/2022

rm(list=ls())
library(data.table)
args = commandArgs(trailingOnly=TRUE)

if (length(args)==0) {
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
} else if (length(args)==1) {
  # default output file
  args[2] = "default.csv"
}

df <- fread(args[1])
print(print(paste('Orig Rows:',dim(df)[1])))


# remove duplicate edges
df <- unique(df)
print(print(paste('Minus Duplicates:',dim(df)[1])))

# remove self loops
df <- df[!V1==V2]
print(print(paste('Minus Selfloops:',dim(df)[1])))

# remove parallel edges
df[,iV1 := V2]
df[,iV2 := V1]
df <- df[!(V1==iV1 & V2==iV2)]
df[,iV1:=NULL];df[,iV2:=NULL]
print(print(paste('Minus Parallel Edges:',dim(df)[1])))

fwrite(df, file=args[2], row.names=FALSE)


