import csv

class csv_importer:
    def __init__(self, db_handler_osm, params, logging):
        self.logging = logging
        self.db_handler_osm = db_handler_osm
        self.params = params
        self.file_postal_office = params['file_postal_office']

    def import_postal(self):
        self.db_handler_osm.create_database()

        print(self.file_postal_office)

        with open(self.file_postal_office) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:

                print(row[1]+", "+row[2]+", "+row[5]+", "+row[12]+", "+row[22]+", "+row[23])
                try:
                    lon = float(row[22].replace(",","."))
                    lat = float(row[23].replace(",","."))
                    self.db_handler_osm.insert(row[0], row[1], lat, lon, row[5], row[6])
                except ValueError:
                    print("Not a float")

            print(f'Processed {line_count} lines.')