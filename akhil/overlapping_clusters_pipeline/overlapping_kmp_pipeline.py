import click
from collections import Counter, defaultdict
from copy import copy

@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help='Clustering output from another method')
@click.option("--network-file", required=True, type=click.Path(exists=True), help='The tsv edgelist of the whole network')
@click.option('--output-path', required=True, type=click.Path(), help ="Output file path")
@click.option('--min-k-core', required=True, type=int, help='Minimum k-value to add overlapping clusters to')
@click.option('--top-n', required=True, type=int, help='Top N total degree nodes to consider for overlapping clusters')
@click.option('--candidate-criterion', required=True, type=click.Choice(['total_degree', 'indegree', 'outdegree']), help='Criterion to choose candidate nodes to add to overlapping clusters')

def main(clustering, network_file, output_path, min_k_core, top_n, candidate_criterion):
 
  node_info = network_to_dict(network_file)
  print('Finished Generating Node Info')
  
  clusters, node_to_cluster_id = clustering_to_dict(clustering)
  print('Finished Generating Clusters')
  
  overlapping_clusters, overlapping_node_info, overlapping_node_to_cluster_id = iterative_OC_generation(clusters, node_info, node_to_cluster_id, min_k_core, top_n, candidate_criterion)
  overlapping_clusters_to_output(output_path, overlapping_clusters)

def iterative_OC_generation(clusters, node_info, node_to_cluster_id, min_k_core, top_n, candidate_criterion):
  degree_map = Counter(node_info[candidate_criterion])
  candidates = [k for k,_ in degree_map.most_common(top_n)]
  candidates.sort(reverse=True, key=lambda n: node_info[candidate_criterion][n])
  overlapping_clusters = copy(clusters)
  overlapping_node_info = copy(node_info)
  overlapping_node_to_cluster_id = copy(node_to_cluster_id)
  
  while True:
    additions = 0
    for node in candidates:
      for cluster_id, cluster_nodes in overlapping_clusters['Core Node Clusters'].items():
        if len(overlapping_node_info['neighbors']['node'].intersection(cluster_nodes)) >= min_k_core and node not in cluster_nodes:
          additions += 1
  
          overlapping_clusters['Full Clusters'][cluster_id].add(node)
          overlapping_clusters['Core Node Clusters'][cluster_id].add(node)
          overlapping_node_to_cluster_id[node].add(cluster_id)
      if additions == 0:
        break

  return overlapping_clusters, overlapping_node_info, overlapping_node_to_cluster_id



def kmp_valid_parsing(clustering, network_file, output_path, min_k_core):
  command = 'pipenv run python3 ~/ERNIE_Plus/Illinois/clustering/eleanor/code/parsing_clusters.py -e ' + network_file + ' -o parsed_' + output_path + ' -c ' + output_path + ' -k ' + min_k_core + ' -p 2'
  print(command)
  os.system(command)

def overlapping_clusters_to_output(output_path, overlapping_clusters):
  output_path_writer = open(output_path, 'w')
  for cluster_id, node_set in overlapping_clusters['Full Clusters'].items():
    for node in node_set:
      output_path_writer.write(cluster_id + ' ' + node + '\n')


def network_to_dict(network_file):
  node_info = defaultdict()
  node_info['neighbors'] = defaultdict(set)
  node_info['total_degree'] = defaultdict(int)
  node_info['indegree'] = defaultdict(int)
  node_info['outdegree'] = defaultdict(int)
  
  network_file_reader = open(network_file, 'r')
  
  line = network_file_reader.readline()
  
  while line != "":
    v1, v2 = line.split('\t')
    v1, v2 = v1.strip(), v2.strip()

    node_info['total_degree'][v1] += 1
    node_info['outdegree'][v1] += 1
    node_info['neighbors'][v1].add(v2)


    node_info['total_degree'][v2] += 1
    node_info['indegree'][v2] += 1
    node_info['neighbors'][v2].add(v1)


    line = network_file_reader.readline()

  return node_info

def clustering_to_dict(clustering):
  clusters = defaultdict()
  clusters['Full Clusters'] = defaultdict(set)
  clusters['Core Node Clusters'] = defaultdict(set)
  clusters['Periphery Node Clusters'] = defaultdict(set)

  node_to_cluster_id = defaultdict(set)
  clustering_reader = open(clustering, 'r')

  line = clustering_reader.readline()

  while line != "":
    node_cluster_info = line.split(',')
    node_id = node_cluster_info[0]
    cluster_id = node_cluster_info[1]
    
    node_to_cluster_id[node_id].add(cluster_id)

    clusters['Full Clusters'][cluster_id].add(node_id)
    if node_cluster_info[2] == 'Core':
      clusters['Core Node Clusters'][cluster_id].add(node_id)
    else:
      clusters['Periphery Node Clusters'][cluster_id].add(node_id)

    line = clustering_reader.readline()

  return clusters, node_to_cluster_id

if __name__ == '__main__':
  main()
