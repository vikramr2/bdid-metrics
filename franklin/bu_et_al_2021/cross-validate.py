import pandas as pd

print('Generating Pandas dataframes...')

# Read CSVs
george_df = pd.read_csv('/srv/local/shared/external/dbid/bu_all.csv')
franklin_df = pd.read_csv('/home/fmoy3/git_repo/franklin/bu_et_al_2021/py_version/fmoy3_bdid_metrics-2022-02-14-07-44-42.csv')

# Drop proportions and cluster_id as George's CSV didn't have these cols
franklin_df.drop(['cluster_id', 'pcp_r_citing_zero', 'pcp_r_citing_nonzero', 'mr_citing', 'pcp_r_cited_zero', 'pcp_r_cited_nonzero', 'mr_cited'], axis=1, inplace=True)

# Rename and reorder to match George's col names
franklin_df.rename(columns={'pub_int_id':'fp','cp_r_citing_zero':'cp_r_citing_pub_zero', 'cp_r_citing_nonzero':'cp_r_citing_pub_nonzero', 'tr_cited':'tr_cited_pub', 'cp_r_cited_nonzero':'cp_r_cited_pub_nonzero', 'cp_r_cited_zero':'cp_r_cited_pub_zero'}, inplace=True)
franklin_df = franklin_df[['fp', 'cp_level', 'cp_r_citing_pub_nonzero', 'cp_r_citing_pub_zero', 'tr_citing', 'tr_cited_pub', 'cp_r_cited_pub_nonzero', 'cp_r_cited_pub_zero']]

# For some reason, George's original DF had nulls
# print(george_df['fp'].isnull()[george_df['fp'].isnull() == True])
george_df.dropna(inplace=True)
george_df['fp'] = george_df['fp'].astype(int)

# Filter to match dataset
george_df_subset = george_df[(george_df['fp'].isin(franklin_df['fp']))]
franklin_df_subset = franklin_df[(franklin_df['fp'].isin(george_df_subset['fp']))]

# Sort both subsets and drop their indices as we only want to check raw data
franklin_df_subset = franklin_df_subset.sort_values('fp').reset_index(drop=True)
george_df_subset = george_df_subset.sort_values('fp').reset_index(drop=True)

# Print results
print('\nGeorge\'s data:')
print(george_df_subset)
print('\nFranklin\'s data:')
print(franklin_df_subset)
print(f'\nAre equal: {franklin_df_subset.equals(george_df_subset)}')