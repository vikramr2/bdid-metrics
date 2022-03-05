-- integer_ids from exosome data that are in the retraction_doi list

SELECT retraction_doi,edcn.integer_id,edcn.year FROM cleaned_rw cr
INNER JOIN dimensions.exosome_dimensions_complete_nodelist edcn
  ON edcn.doi=lower(cr.retraction_doi);

-- integer_ids from exosome data that are in the original_doi list
with cte as(
SELECT edcn.integer_id,edcn.year,
       original_paper_doi, orig_year,
       retraction_doi, retraction_year
FROM cleaned_rw cr
INNER JOIN dimensions.exosome_dimensions_complete_nodelist edcn
  ON edcn.doi=lower(cr.original_paper_doi))
select retraction_year-orig_year from cte;

