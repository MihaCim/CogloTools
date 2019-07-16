import sys
import csv
from src.modules.create_graph.pojo.post import Post
from src.modules.create_graph.utils import utils

class PostHandler:

    def __init__(self):
        self.posts = []

    def is_number(self, str):
        try:
            return float(str)
        except ValueError:
            return None

    def read_postal_offices(self):
        ''' Postal offices are read from csv file and than added to array
        '''
        self.posts = []
        with open('config/List of Postal Offices (geographical location).csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                address = [row[13], row[14], row[15]]
                if (self.is_number(row[22]) != None and self.is_number(row[23]) != None):
                    post = Post(' '.join(address), self.is_number(row[22]), self.is_number(row[23]))
                    self.posts.append(post)

        return self.posts

    def align_nodes_and_posts(self, nodesL):
        '''
        Align post offices with nodes

        :param posts:
        :param nodesL:
        :return:
        '''
        posts = self.read_postal_offices()
        postsNodes = []
        for post in posts:
            minDist = sys.maxsize
            nodeKey = ""
            for key, node in nodesL.items():
                tmpDist = utils.calcDistance(post.latitude, post.longitude, node.lat, node.lon)
                if minDist > tmpDist:
                    minDist = tmpDist
                    nodeKey = key

            tmpNode = nodesL[nodeKey]
            if utils.calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon) < 1:
                print(nodeKey)
                print(post.address)
                print(utils.calcDistance(post.latitude, post.longitude, tmpNode.lat, tmpNode.lon))
                postsNodes.append(nodeKey)
                tmpNode.add_post(post.address)
                nodesL[nodeKey] = tmpNode
        return (nodesL, postsNodes)
