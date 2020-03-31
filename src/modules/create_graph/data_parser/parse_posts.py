
import csv
from pojo.post import Post

class PostHandler:

    def __init__(self):
        self.posts = []

    def is_number(self, str):
        try:
            return float(str)
        except ValueError:
            return None

    def posts_si(self, post_path):
        posts = []
        with open(post_path, encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                #address = [row[13], row[14], row[15]]
                address = [row[0]]
                uuid = [row[1]]
                if (self.is_number(row[2]) != None and self.is_number(row[3]) != None):
                    post = Post(' '.join(address),' '.join(uuid), self.is_number(row[2]), self.is_number(row[3]))
                    posts.append(post)
        return posts

    def posts_hr(self, post_path):
        posts = []
        with open(post_path, encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                address = [row[3], row[4]]
                if (self.is_number(row[7]) != None and self.is_number(row[8]) != None):
                    post = Post(' '.join(address), self.is_number(row[7]), self.is_number(row[8]))
                    posts.append(post)
        return posts

    def read_postal_offices(self, post_paths):
        ''' Postal offices are read from csv file and than added to array
        '''
        self.posts = []
        for name, post_path in post_paths.items():
            if 'si' in name:
                self.posts.extend(self.posts_si(post_path))
            elif 'hr' in name:
                self.posts.extend(self.posts_hr(post_path))

        return self.posts
