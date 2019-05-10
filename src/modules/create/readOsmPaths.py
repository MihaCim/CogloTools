#!/usr/bin/python3

import xml.sax

nodes = {}
ways = []


class MovieHandler(xml.sax.ContentHandler):

    def startElement(self, name, attrs):
       # print("Element start: %s (%d attribute(s))" % (name, len(attrs)))

        if name == "node":
            node = Node()
            if "id" in attrs and "lat" in attrs and "lon" in attrs:
                node.addNode(attrs["id"], attrs["lat"], attrs["lon"])
                nodes[attrs["id"]] = node
        if name == "way":
            self.way = Way()
            print(name)
            for key in dict(attrs):
                print(key + ", " + attrs[key])
        if name == "nd":
            self.way.addNode(attrs["ref"])
            for key in dict(attrs):
             print(key + ", " + attrs[key])



    def endElement(self, name):
        print("Element end: %s" % name)
        if name == "way":
            ways.append(self.way)



    def characters(self, data):
      print("Characters: %s" % data)




class Node:

    def addNode(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon


class Way:
    def __init__(self):
        self.ids = []

    def addNode(self, id):
        self.ids.append(id)

if (__name__ == "__main__"):
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = MovieHandler()
    parser.setContentHandler(Handler)

    parser.parse("stahovica.osm")

    print(len(nodes))
    print(len(ways))

