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
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                    line_count += 1
            print(f'Processed {line_count} lines.')