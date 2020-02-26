

class MockupPartitioning:
    def __init__(self, nodes, edges):
        print("p")
        self.nodes = nodes
        self.edges = edges

    def partitioning_graph(self):
        nodes = ('A6', 'A17', 'A10', 'A8', 'A16', 'A12', 'A18', 'A5')
        nodes = dict()
        for node in self.nodes.items():
            nodes[node["node_id"]] = node
        for edge in self.edges.items():
            #if edge
            print(edge)
