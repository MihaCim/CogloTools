
import csv
from modules.create_graph.pojo.post import Post

class PostHandler:

    def __init__(self):
        self.posts = []

    def is_number(self, str):
        try:
            return float(str)
        except ValueError:
            return None

    def read_postal_offices(self, post_path):
        ''' Postal offices are read from csv file and than added to array
        '''
        self.posts = []
        with open(post_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                address = [row[13], row[14], row[15]]
                if (self.is_number(row[22]) != None and self.is_number(row[23]) != None):
                    post = Post(' '.join(address), self.is_number(row[22]), self.is_number(row[23]))
                    self.posts.append(post)

        return self.posts
