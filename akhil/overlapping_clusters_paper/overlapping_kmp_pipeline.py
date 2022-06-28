import click
from collections import Counter, defaultdict
from copy import copy, deepcopy
import logging
import networkx as nx
import networkx.algorithms.community as nx_comm
import numpy as np
import os 
import overlapping_clusters_stats as ocs 
import pandas as pd
import random
import statistics
import time
from visualization import scatterplot_analysis, histogram_analysis

@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help='Clustering output from another method')
@click.option("--network-file", required=True, type=click.Path(exists=True), help='The tsv edgelist of the whole network')
@click.option('--output-path', required=True, type=click.Path(), help ="Output file path")
@click.option('--min-k-core', required=True, type=int, help='Minimum k-value to add overlapping clusters to')
@click.option('--top-percent', required=True, type=int, help='Top percent of nodes by  total degree o consider for overlapping clusters')
@click.option('--inclusion-criterion', required=True, type=click.Choice(['k', 'mcd']), help='Criterion to include candidate nodes to a cluster')
@click.option("--marker-file", required=False, type=click.Path(exists=True), help='The csv mapping of marker node DOI to ID')

def main(clustering, network_file, output_path, min_k_core, top_percent, inclusion_criterion, marker_file):
  logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
  
  run_oc = True
  display_cluster_stats = True
  save_output = True
  qualifier = '_markers_1percent'
  
  # Parse Marker Node File Data
  marker_nodes, marker_mapping = parse_marker_file(marker_file)
  marker_nodes.append('1002157')

  marker_mapping['1002157'] = 'BLAST'

  original_marker_nodes, original_marker_mapping = parse_marker_file('original_markers.csv')
  logging.info('Finished Parsing Marker Node File')
  
  # Parse KM Validity of Cluster
  kmp_valid_parsing(network_file, 'km_valid_' + str(min_k_core) + str(qualifier) + '.clustering', clustering, min_k_core)
  logging.info('Finished KM Parsing Input Cluster')
  
  # Parse Network Data
  node_info = network_to_dict(network_file)
  G = nx.read_edgelist(network_file, delimiter='\t')
  logging.info('Finished Network Parsing')

  seeds, seed_mapping = parse_marker_file('seed_map.csv')
  logging.info('Finished Seed Parsing')

  # Parse Clustering Data
  clusters, node_to_cluster_id = clustering_to_dict('./test/km_valid_' + str(min_k_core) + str(qualifier) + '.clustering', min_k_core)
  logging.info('Finished Cluster Parsing')
  # Generate Original Cluster by Cluster Stats
  _ = ocs.cluster_analysis('./experiment_2/k_' + str(min_k_core) + str(qualifier) + '_original_cluster_stats.csv', clusters, node_info, is_overlapping=False)
  logging.info('Finished Generating Cluster by Cluster Stats for Original Clusters')

  # Generate Candidates
  candidates = generate_candidates(node_info, top_percent)
  #candidates = set(original_marker_nodes).union(marker_nodes, seeds)
  logging.info('Finished Candidate Generation')
  
  # Run Iterative OC Generation
  oc_start = time.time()
  overlapping_clusters = copy(clusters)
  if run_oc:
    overlapping_clusters, overlapping_node_to_cluster_id  = overlapping_clusters_construction(
        clusters, 
        G, 
        node_info, 
        node_to_cluster_id, 
        top_percent, 
        inclusion_criterion,
        candidates) 
  oc_end = time.time()
  logging.info('Overlapping Clustering Construction Elapsed Time (s): ' + str(oc_end - oc_start))
  logging.info('Finished Overlapping Clustering Generation')
  
  # Save Temp OC Output to File
  if run_oc:
    overlapping_clusters_to_output('./test/oc_output_' + str(min_k_core) + str(qualifier) + '.clustering', overlapping_clusters)
    logging.info('Finished Saving Temporary Output')
    # Check KM-validity of Overlapping Clusters
    
    kmp_valid_parsing(network_file, 'oc_km_valid_' + str(min_k_core) + str(qualifier) + '.clustering', './test/oc_output_' + str(min_k_core) + str(qualifier) + '.clustering', min_k_core)
    logging.info('Finished KM Parsing Overlapping Cluster')
    
    overlapping_clusters, overlapping_node_to_cluster_id = clustering_to_dict('./test/oc_km_valid_' + str(min_k_core) + str(qualifier) + '.clustering', min_k_core)
    logging.info('Finished Overlapping Cluster Parsing')
    
  # Generate Cluster Stats
  if display_cluster_stats:
    cluster_stats(network_file, overlapping_clusters, node_info, G, marker_nodes)
    logging.info('Finished Cluster Stats')
  
  if run_oc:
    # Generate Overlapping Cluster by Cluster Stats
    _ = ocs.cluster_analysis('./experiment_2/k_' + str(min_k_core) + str(qualifier) + '_overlapping_cluster_stats.csv', overlapping_clusters, node_info, is_overlapping=True)
    logging.info('Finished Generating Cluster by Cluster Stats for Overlapping Clusters')
    # Generate Overlapping Cluster Intersection Stats
    _ = ocs.cluster_intersection_analysis('./experiment_2/k_' + str(min_k_core) + str(qualifier) + '_intersection_stats.csv', overlapping_clusters)
    logging.info('Finished Generating Cluster Cluster Intersection Stats for Overlapping Clusters')

  # Save Final OC Output to File
  if save_output:
    overlapping_clusters_to_output(output_path, overlapping_clusters)
    logging.info('Finished Saving Final Output')

'''
Computes statistics for a given clustering

Input:
  network_file str - path to network tsv file 
  clusters {dict} - dictionary of clusters by cluster id
  node_info {dict} -  dictionary of info on nodes in network
  candidates [list] - liest of candidate node ids
Output:
  None - Cluster stats printed to console
  Format: Num Clusters, Num Singleton Nodes, Min Cluster Size, Median Cluster Size, Max Cluster Size, Node Coverage, Edge Coverage, Candidate Node Coverage, Candidate Edge Coverage
'''
def cluster_stats(network_file, clusters, node_info, G, candidates):
  #G = nx.read_edgelist(network_file, delimiter='\t')
  
  num_clusters, num_singletons, min_size, max_size, median_size, node_coverage = basic_cluster_info(clusters, node_info)
  edge_coverage = get_edge_coverage(G, clusters)
  candidate_node_coverage, candidate_edge_coverage = get_coverage_node_list(G, clusters, candidates)
  
  print('Num Clusters:', num_clusters)
  print('Num Singleton Nodes:', num_singletons)
  print('Min Cluster Size:', min_size)
  print('Median Cluster Size:', median_size)
  print('Max Cluster Size:', max_size)
  print('Node Coverage:', node_coverage)
  print('Edge Coverage:', edge_coverage)
  print('Candidate Node Coverage:', candidate_node_coverage)
  print('Candidate Edge Coverage:', candidate_edge_coverage)

'''
Computes basic statistics for a given clustering

Input:
  clusters {dict} - dictionary of clusters by cluster id
  node_info {dict} -  dictionary of info on nodes in network
Output:
  num_clusters int
  num_singletons int
  min_cluster_size int
  max_cluster_size int
  median_cluster_size float
  node_coverage float
'''
def basic_cluster_info(clusters, node_info):
  num_nodes = len(node_info['total_degree'].keys())
  num_clusters = len(clusters['Full Clusters'].keys())

  non_singleton_node_set = [clusters['Full Clusters'][key] for key in clusters['Full Clusters']]
  non_singleton_node_count = len(set().union(*non_singleton_node_set))
  cluster_size_array = [len(clusters['Full Clusters'][key]) for key in clusters['Full Clusters']]
  
  num_singletons = num_nodes - non_singleton_node_count
  min_cluster_size = min(cluster_size_array)
  max_cluster_size = max(cluster_size_array)
  median_cluster_size = statistics.median(cluster_size_array)
  node_coverage = non_singleton_node_count/num_nodes

  return num_clusters, num_singletons, min_cluster_size, max_cluster_size, median_cluster_size, node_coverage

'''
Computes edge coverage of a given clustering

Input:
  G networkx.Graph - networkx representation of input network
  clusters {dict} - dictionary of clusters by cluster id
Output:
  edge_coverage float
'''
def get_edge_coverage(G, clusters):
  total_edges = G.number_of_edges()
  counted_edges = set()
  for c in clusters['Full Clusters'].keys():
    nodes = list(clusters['Full Clusters'][c])
    G_prime = G.subgraph(nodes)
    counted_edges.update(set(G_prime.edges))
    #clusters['modularity'][c] = nx_comm.modularity(G,nodes)
  edge_coverage = len(counted_edges)/total_edges
  return edge_coverage

'''
Computes node and edge coverage of a given clustering for a specific list of nodes in the network

Input:
  G networkx.Graph - networkx representation of input network
  clusters {dict} - dictionary of clusters by cluster id
  candidates [list] list of node ids of the subset of nodes to check coverage
Output:
  node_coverage float
  edge_coverage float
'''
def get_coverage_node_list(G, clusters, candidates):
  candidates_in_cluster = set()
  total_edges = len(set(G.edges(candidates)))
  counted_edges = set()
  for c in clusters['Full Clusters'].keys():
    nodes = list(clusters['Full Clusters'][c])
    candidates_in_cluster.update(set(nodes).intersection(set(candidates)))
    G_prime = G.subgraph(nodes)
    counted_edges.update(set(G_prime.edges(candidates)))
  node_coverage = len(candidates_in_cluster)/len(candidates)
  edge_coverage = len(counted_edges)/total_edges
  return node_coverage, edge_coverage

'''
Returns list of candidate node ids given top n percent of nodes in network by total degree

Input:
  node_info {dict} - dictionary of info on nodes in network
  top_percent int - integer representing top n percent of nodes to consider based on total degree
Output:
  candidates [list] - list of candidate node ids
'''
def generate_candidates(node_info, top_percent):
  degree_map = Counter(node_info['total_degree'])
  #candidates = list(node_info['total_degree'].keys())
  #size = len(candidates)
  #candidates = random.sample(candidates, int((top_percent*len(node_info['total_degree'].keys()))/100))
  candidates = [k for k,_ in degree_map.most_common(int((top_percent*len(node_info['total_degree'].keys()))/100))]
  # changed reverse=True to reverse=False
  candidates.sort(reverse=False, key=lambda n: node_info['total_degree'][n])
  return candidates

'''
Overlapping clustering method that adds candidate nodes to clusters based on some inclusion criterion

Input:
  clusters {dict} - dictionary of clusters by cluster id
  node_info {dict} - dictionary of info on nodes in network
  node_to_cluster_id {dict} - dictionary of nodes mapped to the disjoint cluster id they are part of
  top_percent int - integer representing top n percent of nodes to consider based on total degree
  inclusion_criterion str - criteria to include a node into a cluster {k, mcd}
  candidates [list] list of node ids of the subset of nodes to check coverage
Output:
  overlapping_clusters {dict} - dictionary of overlapping clusters by cluster id
  overlapping_node_to_cluster_id {dict} dictionary of nodes mapped to the overlapping cluster ids they are part of

'''
def overlapping_clusters_construction(clusters, G, node_info, node_to_cluster_id, top_percent, inclusion_criterion, candidates):
  overlapping_clusters = copy(clusters)
  overlapping_node_to_cluster_id = copy(node_to_cluster_id)
  l = G.size()
  for cluster_id, cluster_nodes in overlapping_clusters['Core Node Clusters'].items():
    subgraph = G.subgraph(cluster_nodes)
    ls = subgraph.size()
    ds = sum([node_info['total_degree'][node] for node in cluster_nodes])
    modularity = ls/l - (ds/(2*l))**2
    nodes_added = 0
    for node in candidates:
      if len(node_info['neighbors'][node].intersection(cluster_nodes)) >= overlapping_clusters[inclusion_criterion][cluster_id] and node not in cluster_nodes:
        new_modularity = get_modularity(ls, ds, l, modularity, node_info, node)
        if new_modularity > 0:
          overlapping_clusters['Full Clusters'][cluster_id].add(node)
          #overlapping_clusters['Core Node Clusters'][cluster_id].add(node)
          overlapping_node_to_cluster_id[node].add(cluster_id)
          modularity = new_modularity
          nodes_added += 1

    overlapping_clusters['modularity'][cluster_id] = modularity

  return overlapping_clusters, overlapping_node_to_cluster_id

'''
Iteratively updates the modularity given a new node assigned to the cluster
Modified from Eleano Wedell's modularity code in eleanor/code/parsing_clusters_strict.py

Input:
  ls int
  ds int
  l int 
  modularity float - current modularity of cluster
  node_info {dict} - info on all nodes in network
  node int - node id of node added to cluster

Output:
  modularity float - updated modularity of cluster
'''
def get_modularity(ls, ds, l, modularity, node_info, node):
  ds += node_info['total_degree'][node]
  return (ls/l - (ds/(2*l))**2)


'''
Wrapper function to run parsing_clusters_strict.py in eleanor/code
Currently defaults to p = 0 (No periphery nodes)

Input:
  network_file str - path to network tsv file 
  output_path str  - output path to save parsed clustering
  clustering str - path to original clustering file
  min_k_core int - minimum k value to parse
Output:
  None
'''
def kmp_valid_parsing(network_file, output_path, clustering, min_k_core):
  command = 'pipenv run python3 ~/ERNIE_Plus/Illinois/clustering/eleanor/code/parsing_clusters_strict.py -e ' + network_file + ' -o ./test/' + output_path + ' -c ./' + clustering  + ' -k ' + str(min_k_core) + ' -p 0' 
  os.system(command)

'''
Wrapper function to run modified_IKC.py 
the modified IKC file mirrors the IKC.py in eleanor/code expect the input is a tsv network

Input:
  network_file str - path to network tsv file 
  k int - minimum k value to parse
Output:
  None
'''
def IKC(network_file, k):
  command = 'pipenv run time python3 modified_IKC.py -e ' + network_file + ' -o ./experiment_0/IKC_' + str(k) + '.clustering -k ' + str(k)
  os.system(command)

'''
Method to save overlapping cluster to a clustering file

Input:
  output_path str - path to output clustering file
  overlapping_clusters {dict} - dictionary of overlapping clusters by cluster id
Output:
  None
'''
def overlapping_clusters_to_output(output_path, overlapping_clusters):
  output_path_writer = open(output_path, 'w')
  for cluster_id, node_set in overlapping_clusters['Full Clusters'].items():
    for node in node_set:
      output_path_writer.write(cluster_id + ' ' + node + '\n')

'''
Method to save overlapping cluster to a clustering file

Input:
  marker_file str - file to csv of marker nodes
Output:
  marker_list [list] - list of marker nodes by id
  mapping {dict} - mapping of marker ids to their DOIs
'''
def parse_marker_file(marker_file):
  mapping = defaultdict(str)
  df = pd.read_csv(marker_file)
  markers = df['integer_id']
  for index, n_id in enumerate(df['integer_id']):
    mapping[str(n_id)] = df['doi'][index]
  marker_list = list(map(str, markers.tolist()))
  return marker_list, mapping

'''
Method to extract network data from network file

Info Collected:
  neighbors - set of neighbors of a given node
  total_degree - total degree of a given node
  indegree - citations given to a specific node
  outdegree - references for a given node
  candidate_type - type of node {original, candidate}

Input:
  network_file str - file path to network file to parse
Output:
  node_info {dict} dictionary of info on each node in the network 
'''
def network_to_dict(network_file):
  node_info = defaultdict()
  node_info['neighbors'] = defaultdict(set)
  node_info['total_degree'] = defaultdict(int)
  node_info['indegree'] = defaultdict(int)
  node_info['outdegree'] = defaultdict(int)
  node_info['candidate_type'] = defaultdict(str)
  
  network_file_reader = open(network_file, 'r')
  
  line = network_file_reader.readline()
  
  while line != "":
    v1, v2 = line.split('\t')
    v1, v2 = v1.strip(), v2.strip()
    
    node_info['total_degree'][v1] += 1
    node_info['outdegree'][v1] += 1
    node_info['neighbors'][v1].add(v2)
    node_info['candidate_type'][v1] = 'original'  

    node_info['total_degree'][v2] += 1
    node_info['indegree'][v2] += 1
    node_info['neighbors'][v2].add(v1)
    node_info['candidate_type'][v2] = 'original'

    line = network_file_reader.readline()

  return node_info

'''
Method to extract cluster data from a clustering file

Info Collected:
  Full Clusters - set of all nodes in a given cluster
  Core Node Clusters - set of all core nodes in a given cluster
  Periphery Node Clusters - set of all periphery nodes in a given cluster
  mcd - minimum core degree of a given cluster
  k - k value of a given cluster 
Input:
  clustering str - file path to clustering file to parse
  min_k_core int - minimum k value to parse
Output:
  clusters {dict} - dictionary of clusters by cluster id
  node_to_cluster_id {dict} - dictionary of node ids mapped to their disjoint cluster id
'''
def clustering_to_dict(clustering, min_k_core):
  num_neg_mod = 0
  num_pos_mod = 0
  clusters = defaultdict()
  clusters['Full Clusters'] = defaultdict(set)
  clusters['Core Node Clusters'] = defaultdict(set)
  clusters['Periphery Node Clusters'] = defaultdict(set)
  clusters['mcd'] = defaultdict(int)
  clusters['k'] = defaultdict(int)
  clusters['modularity'] = defaultdict(float)

  node_to_cluster_id = defaultdict(set)
  clustering_reader = open(clustering, 'r')

  line = clustering_reader.readline()

  while line != "":
    node_cluster_info = line.split(',')
    node_id = node_cluster_info[0]
    cluster_id = node_cluster_info[1]
    
    node_to_cluster_id[node_id].add(cluster_id)
    
    clusters['Full Clusters'][cluster_id].add(node_id)
    clusters['Core Node Clusters'][cluster_id].add(node_id)
    clusters['mcd'][cluster_id] = min_k_core #int(node_cluster_info[4])
    clusters['k'][cluster_id] = min_k_core 
    clusters['modularity'][cluster_id] = float(node_cluster_info[3])
    if float(node_cluster_info[3]) < 0:
      num_neg_mod += 1
    else:
      num_pos_mod += 1

    if node_cluster_info[2] == 'Core':
      clusters['Core Node Clusters'][cluster_id].add(node_id)
    else:
      clusters['Periphery Node Clusters'][cluster_id].add(node_id)

    line = clustering_reader.readline()
  print('Number of Clusters with Negative Modularity:', num_neg_mod)
  print('Number of Clusters with Positive Modularity:', num_pos_mod)
  return clusters, node_to_cluster_id

if __name__ == '__main__':
  main()

