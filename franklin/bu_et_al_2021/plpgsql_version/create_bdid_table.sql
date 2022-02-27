CREATE TABLE IF NOT EXISTS fmoy3.exosome_bdid_metrics (
    cited_integer_id INT NOT NULL,
    cp_level INT NOT NULL,
    cp_r_citing_equal_zero INT NOT NULL,
    cp_r_citing_not_zero INT NOT NULL,
    tr_citing INT NOT NULL,
    pcp_r_citing_equal_zero DECIMAL(10,4) NOT NULL,
    pcp_r_citing_not_zero DECIMAL(10,4) NOT NULL,
    mr_citing DECIMAL(10,4) NOT NULL,
    cp_r_cited_equal_zero INT NOT NULL,
    cp_r_cited_not_zero INT NOT NULL,
    tr_cited INT NOT NULL,
    pcp_r_cited_equal_zero DECIMAL(10,4) NOT NULL,
    pcp_r_cited_not_zero DECIMAL(10,4) NOT NULL,
    mr_cited DECIMAL(10,4) NOT NULL,
    PRIMARY KEY (cited_integer_id)
);