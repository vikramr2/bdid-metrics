CREATE OR REPLACE PROCEDURE fmoy3.collect_bdid_data_full_scale()
LANGUAGE plpgsql
AS $$
DECLARE
    focal_int_id INT;
    citing_int_id INT;
    cp_level_count INT;
    r_citing INT;
    r_cited INT;
    cp_r_citing_zero INT;
    cp_r_cited_zero INT;
    cp_r_citing_nonzero INT; /* Tracks count of R[citing_pub] > 0 */
    cp_r_cited_nonzero INT;  /* Tracks count of R[cited_pub] > 0 */
    pcp_r_citing_zero DECIMAL(10,4);
    pcp_r_cited_zero DECIMAL(10,4);
    pcp_r_citing_nonzero DECIMAL(10,4);
    pcp_r_cited_nonzero DECIMAL(10,4);
    tr_citing_count INT;
    tr_cited_count INT;
    mr_citing_pub DECIMAL(10,4);
    mr_cited_pub DECIMAL(10,4);
    inserts_staged INT DEFAULT 0;
BEGIN
    /* For each publication in the exosome dataset that has been cited 100 < x < 1000 times */
    FOR focal_int_id IN 
        SELECT integer_id
        FROM dimensions.exosome_1900_2010_sabpq_nodelist
    LOOP
        cp_level_count := (SELECT in_degree FROM dimensions.exosome_1900_2010_sabpq_nodelist WHERE cited_integer_id = focal_int_id);
        cp_r_citing_zero := 0;
        cp_r_citing_nonzero := 0;
        cp_r_cited_zero := 0;
        cp_r_cited_nonzero := 0;
        tr_citing_count := 0;
        tr_cited_count := 0;
        
        

        /* Insert into dedicated BDID metrics table */
        INSERT INTO fmoy3.exosome_bdid_metrics VALUES (
            focal_int_id,
            cp_level_count,
            cp_r_citing_zero,
            cp_r_citing_nonzero,
            tr_citing_count,
            pcp_r_citing_zero,
            pcp_r_citing_nonzero,
            mr_citing_pub,
            cp_r_cited_zero,
            cp_r_cited_nonzero,
            tr_cited_count,
            pcp_r_cited_zero,
            pcp_r_cited_nonzero,
            mr_cited_pub
        );


        /* Commit every 100 inserts */
        inserts_staged := inserts_staged + 1;
        IF inserts_staged % 100 = 0 THEN
            COMMIT;
        END IF;

    END LOOP;
    COMMIT;
END;
$$; 

/* SELECT fmoy3.collect_bdid_data(); */
/* DROP PROCEDURE IF EXISTS fmoy3.collect_bdid_data; */