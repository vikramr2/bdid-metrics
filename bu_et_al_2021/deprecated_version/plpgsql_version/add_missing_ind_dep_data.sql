CREATE OR REPLACE PROCEDURE fmoy3.add_missing_ind_dep_data()
LANGUAGE plpgsql
AS $$
DECLARE
    focal_int_id INT;
    citing_int_id INT;
    r_cited INT;
    cp_r_cited_zero INT;
    cp_r_cited_nonzero INT;  /* Tracks count of R[cited_pub] > 0 */
    pcp_r_cited_zero DECIMAL(10,4);
    pcp_r_cited_nonzero DECIMAL(10,4);
    tr_cited_count INT;
    mr_cited_pub DECIMAL(10,4);
    inserts_staged INT DEFAULT 0;
BEGIN
    /* For each publication in the exosome dataset that has been cited 100 < x < 1000 times */
    FOR focal_int_id IN 
        SELECT cited_integer_id
        FROM fmoy3.exosome_pubs_with_cp_between_100_1000_mat
    LOOP
        cp_r_cited_zero := 0;
        cp_r_cited_nonzero := 0;
        tr_cited_count := 0;
        /* For each publication that cites the publication we're currently focusing on */
        FOR citing_int_id IN 
            SELECT citing_integer_id FROM dimensions.exosome_1900_2010_sabpq_deduplicated 
            WHERE cited_integer_id = focal_int_id 
        LOOP
            r_cited := (SELECT COUNT(*) FROM dimensions.exosome_1900_2010_sabpq_deduplicated
                        WHERE citing_integer_id = citing_int_id AND cited_integer_id IN
                        (SELECT cited_integer_id FROM dimensions.exosome_1900_2010_sabpq_deduplicated
                        WHERE citing_integer_id = focal_int_id));
            
            /* Accumulate TR[cited] */
            tr_cited_count := tr_cited_count + r_cited;
            
            /* Increment CP counters as necessary for the focused publication */
            IF r_cited = 0 THEN
                cp_r_cited_zero := cp_r_cited_zero + 1;
            ELSIF r_cited > 0 THEN
                cp_r_cited_nonzero := cp_r_cited_nonzero + 1;
            ELSE
                RAISE NOTICE 'r_cited is an invalid value';
            END IF;
        END LOOP;
        
        /* Calculate proportions */
        pcp_r_cited_zero := cp_r_cited_zero::DECIMAL / (cp_r_cited_zero + cp_r_cited_nonzero);
        pcp_r_cited_nonzero := cp_r_cited_nonzero::DECIMAL / (cp_r_cited_zero + cp_r_cited_nonzero);
        mr_cited_pub := tr_cited_count::DECIMAL / (cp_r_cited_zero + cp_r_cited_nonzero);
        
        /* Insert into dedicated BDID metrics table */
        UPDATE fmoy3.exosome_bdid_metrics SET
            cp_r_cited_equal_zero = cp_r_cited_zero,
            cp_r_cited_not_zero = cp_r_cited_nonzero,
            tr_cited = tr_cited_count,
            pcp_r_cited_equal_zero = pcp_r_cited_zero,
            pcp_r_cited_not_zero = pcp_r_cited_nonzero,
            mr_cited = mr_cited_pub
            WHERE cited_integer_id = focal_int_id;


        /* Commit every 100 inserts */
        inserts_staged := inserts_staged + 1;
        IF inserts_staged % 100 = 0 THEN
            COMMIT;
        END IF;

    END LOOP;
    COMMIT;
END;
$$; 

/* CALL fmoy3.add_missing_ind_dep_data(); */
/* DROP PROCEDURE IF EXISTS fmoy3.add_missing_ind_dep_data; */