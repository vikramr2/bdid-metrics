import networkx as nx
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Generate the graph
    G = nx.star_graph(10)
    L = nx.line_graph(G)
    
    # Draw the graph
    # nx.draw_networkx(L, node_size=200)
    # plt.show()
    
    # Output the edge list
    nx.write_edgelist(G, path='output.csv', delimiter=",", data=False)