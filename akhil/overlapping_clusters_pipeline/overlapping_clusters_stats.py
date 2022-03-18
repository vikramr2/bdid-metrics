import pandas as pd


def basic_cluster_stats(clusters):
  num_clusters = len(clusters['Full Clusters'].keys())
  size_distribution = pd.Series([len(nodes) for _, nodes in clusters['Full Clusters']]).describe()
  return num_clusters, size_distribution
  

