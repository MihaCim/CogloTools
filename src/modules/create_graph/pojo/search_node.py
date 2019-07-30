
class SearchNode:

    def __init__(self, node_id, post_id=None, is_post=False, lat=None, lon=None, address=None):
        self.node_id = node_id
        self.is_post = is_post
        self.post_id = post_id
        self.lat = lat
        self.lon = lon
        self.address = address

    def set_lat_lon(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def set_address(self, address):
        self.address = address

