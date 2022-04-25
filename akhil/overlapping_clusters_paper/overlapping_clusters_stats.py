from collections import Counter, defaultdict
import pandas as pd
import statistics

def basic_cluster_stats(clusters):
  num_clusters = len(clusters['Full Clusters'].keys())
  size_distribution = pd.Series([len(nodes) for _, nodes in clusters['Full Clusters'].items()]).describe()
  return num_clusters, size_distribution

def neighbor_analysis(overlapping_clusters, original_clusters, candidates, node_info, overlapping_node_to_cluster_id, original_node_to_cluster_id, candidate_criterion):
  num_non_added_nodes = 0
  neighbor_info = defaultdict(list)

  for index, candidate in enumerate(candidates):
    all_cluster_ids = overlapping_node_to_cluster_id[candidate]
    original_cluster_id = None
    if candidate in original_node_to_cluster_id:
      original_cluster_id = list(original_node_to_cluster_id[candidate])[0]
    non_singleton_clusters = []

    for c_id in all_cluster_ids:
      if len(overlapping_clusters['Full Clusters'][c_id]) > 0:
        non_singleton_clusters.append(overlapping_clusters['Full Clusters'][c_id])
    if len(non_singleton_clusters) > 0 and original_cluster_id is not None:
      proportion_neighbors_original = proportion_neighbors_original_clusters(original_clusters['Full Clusters'][original_cluster_id], candidate, node_info['neighbors'][candidate])
      proportion_neighbors_overlapping = proportion_neighbors_all_clusters(non_singleton_clusters, candidate, node_info['neighbors'][candidate])
      neighbor_info['proportion_neighbors_overlapping_clusters'].append(proportion_neighbors_overlapping)
      neighbor_info['proportion_neighbors_original_clusters'].append(proportion_neighbors_original)
      neighbor_info['proportion_neighbor_coverage_increase'].append((proportion_neighbors_overlapping-proportion_neighbors_original)/proportion_neighbors_original)
      neighbor_info[candidate_criterion].append(node_info[candidate_criterion][candidate])
      neighbor_info['degree_rank'].append(index)
    else:
      num_non_added_nodes += 1

  return neighbor_info, num_non_added_nodes


def proportion_neighbors_original_clusters(original_cluster, node, neighbors):
  return float(len(neighbors.intersection(original_cluster))/len(neighbors))

def proportion_neighbors_all_clusters(all_clusters, node, neighbors):
  total_clusters = set().union(*all_clusters)
  return float(len(neighbors.intersection(total_clusters))/len(neighbors))

def node_placement_frequency(clusters, candidates, mapping, node_placement_file):
  writer = open(node_placement_file, 'w')
  
  placement_frequency = defaultdict(int)
  for node in candidates:
    placement_frequency[node] = 0
  
  for c_id, node_set in clusters['Full Clusters'].items():
    for node in node_set:
      if node in candidates:
        placement_frequency[node] += 1
  
  placement_frequency_sorted = dict(sorted(placement_frequency.items(), key=lambda item: item[1], reverse=True))
  
  for k,v in placement_frequency_sorted.items():
    writer.write(str(mapping[k]) +  ': ' + str(v) + '\n')

  writer.close()
  return [placement_frequency[n_id] for n_id in placement_frequency.keys() if n_id in candidates]
  

def edges_added(node, cluster, node_info):
  return len(node_info['neighbors'][node].intersection(cluster))

# Tier Analysis Involves In Degree
def tier_analysis(clusters, node_info, candidates):
  cluster_tier_info = defaultdict(list)
  node_tier_info = defaultdict(list)
  for cluster_id in clusters['Full Clusters']:
    citations = [(n, node_info['indegree'][n]) for n in clusters['Full Clusters'][cluster_id]]
    citations.sort(reverse=True, key = lambda n: n[1])
    threshold_count = int(0.1*len(clusters['Full Clusters'][cluster_id]))
    threshold_value = citations[threshold_count][1]
    greater_than_threshold_count = 0
    for node in clusters['Full Clusters'][cluster_id]:
      if node_info['indegree'][node] >= threshold_value:
        greater_than_threshold_count += 1
    if greater_than_threshold_count > threshold_count:
      threshold_value += 1

    node_tiers = [0, 0, 0]
    for node in clusters['Full Clusters'][cluster_id].intersection(set(candidates)):
        if node_info['indegree'][node] >= threshold_value:
          node_tier_info[node].append(1)
          node_tiers[0] += 1
        elif node_info['indegree'][node] == 0:
          print(node_info['total_degree'][node], node_info['outdegree'][node])
          node_tier_info[node].append(3)
          node_tiers[2] += 1
        else:
          node_tier_info[node].append(2)
          node_tiers[1] += 1


    cluster_tier_info['Tier 1'].append(node_tiers[0])
    cluster_tier_info['Tier 2'].append(node_tiers[1])
    cluster_tier_info['Tier 3'].append(node_tiers[2])
    cluster_tier_info['Cluster Size'].append(len(clusters['Full Clusters'][cluster_id]))

  aggregate_node_tier_info = defaultdict(list)

  for node, tiers in node_tier_info.items():
    tier_frequency = Counter(tiers)
    aggregate_node_tier_info['node_id'].append(node)
    aggregate_node_tier_info['degree'].append(node_info['total_degree'][node])
    aggregate_node_tier_info['tier_1_count'].append(tier_frequency[1])
    aggregate_node_tier_info['tier_2_count'].append(tier_frequency[2])
    aggregate_node_tier_info['tier_3_count'].append(tier_frequency[3])
    aggregate_node_tier_info['average_tier'].append(sum(tiers)/len(tiers))

    aggregate_node_tier_info['node_type'].append(node_info['candidate_type'][node])
  
  print('Tier 1 Count:', sum(aggregate_node_tier_info['tier_1_count']), 
        'Tier 2 Count:', sum(aggregate_node_tier_info['tier_2_count']), 
        'Tier 3 Count:', sum(aggregate_node_tier_info['tier_3_count']))

  return cluster_tier_info, aggregate_node_tier_info

def cluster_intersection_analysis(clusters):
  intersection_stats = defaultdict(list)

  for index1, c_id in enumerate(clusters['Full Clusters']):
    for index2, c_id2 in enumerate(clusters['Full Clusters']):
      if index1 < index2:
        c1 = clusters['Full Clusters'][c_id]
        c2 = clusters['Full Clusters'][c_id2]
        intersect = c1.intersection(c2)
        intersection_stats['size'].append(len(intersect))
        intersection_stats['sum'].append(len(c1) + len(c2))
        intersection_stats['diff'].append(abs(len(c1) - len(c2)))

  print('Min Intersection Size', min(intersection_stats['size']))
  print('Median Intersection Size', statistics.median(intersection_stats['size']))
  print('Max Intersection Size', max(intersection_stats['size']))
  return intersection_stats

