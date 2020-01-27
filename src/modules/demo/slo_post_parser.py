
import csv
class Post:
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon


class SloPostParser:
    def __init__(self, path='./data/post_slo.csv'):
        self.filepath = path
        self.postlist = []

    def parse_file(self):
        with open(self.filepath, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                self.parse_row(row)
        print("Parsed file, extracted {} posts.".format(len(self.postlist)))

    def parse_row(self, row):
        post_name = "{}-{}".format(row[0], row[3]).replace(' ', '')
        lat = row[-7]
        lon = row[-6]
        self.postlist.append(Post(post_name, lat, lon))



if __name__ == '__main__':
    parser = SloPostParser()
    parser.parse_file()
