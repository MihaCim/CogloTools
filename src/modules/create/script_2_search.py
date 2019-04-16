

class search_shortest_path:
    def __init__(self, db_handler_osm, params, logging):
        self.logging = logging
        self.db_handler_osm = db_handler_osm
        self.params = params
        self.file_postal_office = params['file_postal_office']

    def search(self):
        print("aa")