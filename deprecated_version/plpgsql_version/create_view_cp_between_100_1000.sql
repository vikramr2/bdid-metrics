CREATE MATERIALIZED VIEW fmoy3.exosome_pubs_with_cp_between_100_1000_mat AS
    SELECT cited_integer_id, COUNT(citing_integer_id) AS cp
    FROM dimensions.exosome_1900_2010_sabpq_deduplicated
    GROUP BY cited_integer_id
    HAVING COUNT(citing_integer_id) > 100 AND COUNT(citing_integer_id) < 1000;

/* REFRESH MATERIALIZED VIEW fmoy3.exosome_pubs_with_cp_between_100_1000_mat */
/* DROP VIEW IF EXISTS fmoy3.exosome_pubs_with_cp_between_100_1000_mat */