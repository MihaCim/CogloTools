import xml.sax
import networkx as nx
from src.modules.create_graph.data_parser.parse_osm import OsmParsers

class DataHandler():

    def __init__(self):
        # create_graph an XMLReader

        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = OsmParsers()
        parser.setContentHandler(handler)

        parser.parse("data/test_export.osm")

        self.ways = handler.ways
        self.nodes = handler.nodes

    def graph_viz(self):
        G = nx.Graph()
        n = set()

        for edge in self.ways:
            l = edge.get_all_nodes()
            if l[0] not in n:
                G.add_node(l[0], pos=(self.nodes[l[0]].lat, self.nodes[l[0]].lon))
            if l[1] not in n:
                G.add_node(l[1], pos=(self.nodes[l[1]].lat, self.nodes[l[1]].lon))
            G.add_edge(l[0], l[1], weight=edge.distance)
            n.add(l[0])
            n.add(l[1])
        return G



