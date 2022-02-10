import networkx as nx
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Generate the graph
    # G = nx.star_graph(10)
    # L = nx.line_graph(G)
    
    # temp graph
    # G = nx.Graph()
    # elist = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (5, 8), (3,7)]
    # G.add_edges_from(elist)
    # L = nx.line_graph(G)
    
    # temp graph 2
    G = nx.Graph()
    elist = [(1, 2), (1, 3), (1, 4), (4, 2), (2, 3), (3, 5), (5,6), (5, 9), (6, 9), (6, 8), (8, 9)]
    G.add_edges_from(elist)
    
    # Transform the graph and relabel nodes
    L = nx.line_graph(G)
    e = nx.edges(L)
    elist = []
    dict_e = {}
    c = 0
    
    for i in e:
        if i[0] not in dict_e:
            dict_e[i[0]] = c
            c += 1
        if i[1] not in dict_e:
            dict_e[i[1]] = c
            c += 1
        elist.append((dict_e[i[0]], dict_e[i[1]]))
    
    
    # Create new graph where new graph = line graph
    G = nx.Graph()
    G.add_edges_from(elist)
    
    # Draw the graph
    nx.draw_networkx(G, node_size=200)
    plt.show()
    
    # Output the edge list
    nx.write_edgelist(G, path='output.csv', delimiter=",", data=False)