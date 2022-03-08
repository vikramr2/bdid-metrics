# Script to join cleaned_rw data with exosome network to identify
# retracted articles in the network. George Chacko 3/8/2022
# needs to be run with Rscript for the readline part to work

library(RPostgres); library(data.table)

# User supplied parameters

cat("enter_host_address: ")
ha <- readLines("stdin", n=1)
cat("You entered hostname and address")
cat("\n")

cat("userid?: ")
me <- readLines("stdin", n=1)
cat("userid entered")
cat("\n")

cat("password?: ")
pw <- readLines("stdin", n=1)
cat("password entered")
cat("\n")

cat("port no?: ")
pn <- readLines("stdin", n=1)
cat("ok have port no")
cat("\n")

cat("database_name?: ")
db <- readLines("stdin", n=1)
cat("ok..will try connecting")
cat("\n")
Sys.sleep(3)

con <- dbConnect(RPostgres::Postgres(),dbname=db,host=ha, user=me, port=pn, password=pw)
# dbListTables(con)

# gets the set of nodes in the exosome network that represent publications that
# were retracted.

dbGetQuery(con,"SELECT dedcn.integer_id,dedcn.doi FROM dimensions.exosome_dimensions_complete_nodelist dedcn
INNER JOIN chackoge.cleaned_rw ccr ON ccr.original_paper_doi=lower(dedcn.doi)")

# get original paper dois joined with integer_ids
ex_nl_orig_retractions <- dbGetQuery(con,
"WITH cte AS(
SELECT original_paper_doi, orig_year, retraction_doi, retraction_year
FROM chackoge.cleaned_rw
WHERE original_paper_doi IS NOT NULL
AND original_paper_doi NOT IN ('Unavailable', 'unavailable'))
SELECT cte.original_paper_doi, cte.orig_year, cte.retraction_doi, cte.retraction_year
	edcn.doi, edcn.year, edcn.integer_id
FROM cte
INNER JOIN exosome_dimensions_complete_nodelist edcn
ON edcn.doi=lower(cte.original_paper_doi)")

ex_nl <- dbGetQuery(con,"SELECT * FROM exosome_dimensions_complete_nodelist")

dbDisconnect(con)
setwd('~/Desktop/Retractions')
fwrite(ex_nl_orig_retractions,file='ex_orig_retractions.csv')
fwrite(ex_nl,file='ex_nl.csv')
### Alternatively
# dbSendQuery creates a remote object as far as I can tell
#ex_nl_orig_retractions <- dbSendQuery(con,
#"WITH cte AS(
#SELECT original_paper_doi, orig_year 
#FROM chackoge.cleaned_rw
#WHERE original_paper_doi IS NOT NULL
#AND original_paper_doi NOT IN ('Unavailable', 'unavailable'))
#SELECT cte.original_paper_doi, cte.orig_year, 
#	edcn.doi, edcn.year, edcn.integer_id
#FROM cte
#INNER JOIN exosome_dimensions_complete_nodelist edcn
#ON edcn.doi=lower(cte.original_paper_doi)")

# dbFetch retrieves it and should be used for chunked retrieves of large results
# enor <- dbFetch(ex_nl_orig_retractions, n= 25)

# Clean up
#dbClearResult(ex_nl_orig_retractions)
#dbDisconnect(con)


