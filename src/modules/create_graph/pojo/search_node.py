
class SearchNode:

    def __init__(self, node_id, post_id=None, is_post=False, lat=None, lon=None, address=None, post=None):
        self.node_id = node_id
        self.is_post = is_post
        self.post_id = post_id
        self.lat = lat
        self.lon = lon
        self.address = address
        self.post = post
        self.tagged = {}

    def set_lat_lon(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def set_address(self, address):
        self.address = address

    def is_empty_tagged(self):
        return len(self.tagged) > 0

    def isTaggedby(self, start_node_id):
        if start_node_id in self.tagged:
            return True
        return False

    def tag_filter(self):
        id,dist = min(self.tagged.items(), key=lambda x: x[1])
        return id

    def addTag(self, tuple):
        start_node_id, current_dist = tuple
        self.tagged[start_node_id] = current_dist


