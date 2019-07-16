class FrontData:

    def __init__(self, origin_dist, prev_posts, eps_history):
        self.origin_dist = origin_dist
        self.prev_posts = prev_posts
        self.eps_history = eps_history

    def has_traversed(self, n_id):
        """
        Checks if node_id is in the history of this node.
        """
        for hist_node_id, hist_node_dist_origin in self.eps_history:
            if hist_node_id == n_id:
                return True
        return False
