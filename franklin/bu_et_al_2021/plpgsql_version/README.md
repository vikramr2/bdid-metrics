# SQL DDLs and Functions for Bu et al. (2021)
This folder contains all the SQL files used to collect metrics related to Bu et al. (2021).
# Contents
- [`add_missing_ind_dep_data.sql`](add_missing_ind_dep_data.sql): PL/PGSQL procedure that updated calculations from `collect_bdid_data.sql`.
- [`collect_bdid_data.sql`](collect_bdid_data.sql): This file contains a PL/PGSQL procedure that was used to calculate the various metrics proposed in Bu et al. (2021).
- [`collect_bdid_data_test.sql`](collect_bdid_data_test.sql): Test version of the PL/PGSQL procedure that has print statements and a `limiter` argument.
    - The `limiter` argument specifies how many publications to run calculations for, as opposed to the whole database.
- [`create_bdid_table.sql`](create_bdid_table.sql): Table definition (DDL) for the aforementioned metrics (breadth/depth, independence/dependence, CP/level).
- [`create_view_cp_between_100_1000.sql`](create_view_cp_between_100_1000.sql): This file is the view definition to narrow down the exosome dataset. 
    - The view only includes publications that have been cited between 100-1000 times (non-inclusive).
