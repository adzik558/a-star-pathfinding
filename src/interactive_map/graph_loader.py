import osmnx as ox
G = ox.graph_from_place("Rzeszów, Poland", network_type="drive")
ox.save_graphml(G, "data/rzeszow.graphml")