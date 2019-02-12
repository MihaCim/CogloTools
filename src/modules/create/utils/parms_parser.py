import argparse
from configparser import ConfigParser
import ast


class ParmsParser:
    def __init__(self, args=None):

        self.osm = {}
        self.evaluation = {}
        self.preprocessed = {}
        self.matching_tags = {}

        # program parameters
        parser = argparse.ArgumentParser(description='All in one script for camp data scraping, parsing and processing')
        #required=True,

        parser.add_argument('-Eo2p', '--export_osm2postgres', action='store_true',
                            help='OSM data to nextPin')

        if args is None:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(args)

    def read_config(self, conf_file):
        parser = ConfigParser()
        parser.read(conf_file)
        import json



        self.osm['cache_size'] = parser.get('osm', 'cache_size')
        self.osm['download']=ast.literal_eval(parser.get('osm','download'))
        #self.osm['prefix'] = parser.get('osm', 'prefix')

        self.osm['style_file'] = parser.get('osm', 'style_file')
        self.osm['number_processes'] = parser.get('osm', 'number_processes')

        self.osm['folder'] = parser.get('osm', 'folder')
        self.osm['osm_file'] = parser.get('osm', 'osm_file')
        self.osm['file_postal_office'] = parser.get('osm', 'file_postal')


        SECTIONS = ['osm']
        OPTIONS = ['host', 'dbname', 'user', 'password','port']
        dict = {}
        str = ""
        for section in SECTIONS:
            for candidate in OPTIONS:
                has_option = parser.has_option(section, candidate)
                if has_option:
                    str = str + " " + candidate + "=" + parser.get(section, candidate)
                    if section is 'osm':
                        self.osm[candidate]=parser.get(section, candidate)
            dict[section] = str
            str = ''

        self.osm['conn_string'] = dict['osm']

