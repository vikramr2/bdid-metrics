import networkx as nx
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Read the list
    #G = nx.read_edgelist("citing_cited_network.integer_label.tsv")
    G = nx.read_edgelist("output_leiden.clusters")
    
    # Draw the graph
    nx.draw_networkx(G, node_size=200)
    plt.show()