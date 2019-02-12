
class csv_importer:
    def __init__(self, db_handler_osm, params, logging):
        self.logging = logging
        self.db_handler_osm = db_handler_osm
        self.params = params

    def import_postal(self):