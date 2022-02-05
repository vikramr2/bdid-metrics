CREATE OR REPLACE FUNCTION fmoy3.collect_bdid_data()
RETURNS VOID
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
BEGIN
    /* For each publication in the exosome dataset that has been cited 100 < x < 1000 times */
    FOR focal_int_id IN 
        SELECT cited_integer_id FROM fmoy3.exosome_pubs_with_cp_between_100_1000
    LOOP
        cp_level_count := (SELECT COUNT(*) FROM dimensions.exosome_1900_2010_sabpq_deduplicated WHERE cited_integer_id = focal_int_id);
        cp_r_citing_zero := 0;
        cp_r_citing_nonzero := 0;
        cp_r_cited_zero := 0;
        cp_r_cited_nonzero := 0;
        tr_citing_count := 0;
        tr_cited_count := 0;
        /* For each publication that cites the publication we're currently focusing on */
        FOR citing_int_id IN 
            SELECT citing_integer_id FROM dimensions.exosome_1900_2010_sabpq_deduplicated 
            WHERE cited_integer_id = focal_int_id 
        LOOP
            /* Do these need to be dynamic queries?? */
            r_citing := (SELECT COUNT(*) FROM dimensions.exosome_1900_2010_sabpq_deduplicated 
                        WHERE citing_integer_id = citing_int_id AND cited_integer_id IN 
                        (SELECT cited_integer_id FROM dimensions.exosome_1900_2010_sabpq_deduplicated 
                        WHERE cited_integer_id = focal_int_id AND citing_integer_id <> citing_int_id));
            r_cited := (SELECT COUNT(*) FROM dimensions.exosome_1900_2010_sabpq_deduplicated
                        WHERE citing_integer_id = citing_int_id AND cited_integer_id IN
                        (SELECT cited_integer_id FROM dimensions.exosome_1900_2010_sabpq_deduplicated
                        WHERE citing_int_id = focal_int_id));
            
            /* Accumulate TR[citing] and TR[cited] */
            tr_citing_count := tr_citing_count + r_citing;
            tr_cited_count := tr_cited_count + r_cited;
            
            /* Increment CP counters as necessary for the focused publication */
            IF r_citing = 0 THEN
                cp_r_citing_zero := cp_r_citing_zero + 1;
            ELSE 
                cp_r_citing_nonzero := cp_r_citing_nonzero + 1;
            END IF;
            IF r_cited = 0 THEN
                cp_r_cited_zero := cp_r_cited_zero + 1;
            ELSE
                cp_r_cited_nonzero := cp_r_cited_nonzero + 1;
            END IF;
        END LOOP;
        
        /* Calculate proportions */
        pcp_r_cited_zero := cp_r_cited_zero / (cp_r_cited_zero + cp_r_cited_nonzero);
        pcp_r_cited_nonzero := cp_r_cited_nonzero / (cp_r_cited_zero + cp_r_cited_nonzero);
        pcp_r_citing_zero := cp_r_citing_zero / (cp_r_citing_zero + cp_r_citing_nonzero);
        pcp_r_citing_nonzero := cp_r_citing_nonzero / (cp_r_citing_zero + cp_r_citing_nonzero);
        mr_cited_pub := tr_cited_count / (cp_r_cited_zero + cp_r_cited_nonzero);
        mr_citing_pub := tr_citing_count / (cp_r_citing_zero + cp_r_citing_nonzero);

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

    END LOOP;
END;
$$; 

/* SELECT fmoy3.collect_bdid_data(); */
/* DROP FUNCTION IF EXISTS fmoy3.collect_bdid_data; */