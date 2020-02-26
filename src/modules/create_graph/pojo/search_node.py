
class SearchNode:

    def __init__(self, node_id, post_id=None, is_post=False, lat=None, lon=None, address=None, post=None):
        self.node_id = node_id
        self.is_post = is_post
        self.post_id = post_id
        self.lat = lat
        self.lon = lon
        self.address = address
        self.post = post
        self.__tagged = {}
        self.__tag = None

    def set_lat_lon(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def set_address(self, address):
        self.address = address

    def is_empty_tagged(self):
        return len(self.__tagged) > 0

    def clean_tagged(self):
        self.__tag = None
        self.__tagged = {}

    def isTaggedby(self, start_node_id):
        if start_node_id in self.__tagged:
            return True
        return False

    def tag_filter(self):
        if len(self.__tagged) == 0:
            return (None,None)
        return min(self.__tagged.items(), key=lambda x: x[1])

    def addTag(self, tuple):
        start_node_id, current_dist = tuple
        self.__tagged[start_node_id] = current_dist
        self.__tag = start_node_id

    def getTagId(self):
        return self.__tag
