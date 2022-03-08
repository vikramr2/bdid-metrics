# Script to join cleaned_rw data with exosome network to identify
# retracted articles in the network. George Chacko 3/8/2022

con <- dbConnect(RPostgres::Postgres(),dbname='ernieplus',host='<enter_host_address>',user='<enter_userID>',port=5432, password='<enter_password>')


dbGetQuery(con,"SELECT dedcn.integer_id,dedcn.doi FROM dimensions.exosome_dimensions_complete_nodelist dedcn
INNER JOIN chackoge.cleaned_rw ccr ON ccr.original_paper_doi=lower(dedcn.doi)")

# dbSendQuery creates a remote object as far as I can tell
ex_nl_orig_retractions <- dbSendQuery(con,
"WITH cte AS(
SELECT original_paper_doi, orig_year 
FROM chackoge.cleaned_rw
WHERE original_paper_doi IS NOT NULL
AND original_paper_doi NOT IN ('Unavailable', 'unavailable'))
SELECT cte.original_paper_doi, cte.orig_year, edcn.doi, edcn.year, edcn.integer_id
FROM cte
INNER JOIN exosome_dimensions_complete_nodelist edcn
ON edcn.doi=lower(cte.original_paper_doi)")

# dbFetch retrieves it
enor <- dbFetch(ex_nl_orig_retractions)

# Clean up
dbClearResult(ex_nl_orig_retractions)
dbDisconnect(con)


