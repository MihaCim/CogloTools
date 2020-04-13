import os
import json


class ConfigParser:

    def __init__(self):
        config_path = './modules/create_graph/config/config.json'
        if not os.path.exists(config_path):
            print("File config.json does not exist. Config parser cannot be initialized!")
            exit(1)

        with open(config_path) as config:
            self.json_config = json.load(config)
        config.close()

    def get_pickle_path(self, use_case):
        if use_case == "SLO-HR":
            return self.json_config["slo_hr_pickle_path"]
        elif use_case == "ELTA":
            return self.json_config["elta_pickle_path"]

    def get_graph_path(self, use_case):
        if use_case == "SLO-HR":
            return self.json_config["slo_hr_json_graph_data_path"]
        elif use_case == "ELTA":
            return self.json_config["elta_json_graph_data_path"]
        else:
            print("Error - use_case not defined")

    def get_cross_border_nodes_slo(self, use_case):
        if use_case == "SLO-HR":
            return self.json_config["S1", "S3", "S5"]

    def get_cross_border_nodes_cro(self, use_case):
        if use_case == "SLO-HR":
            return self.json_config["H5", "H3", "H1"]

    def get_msb_few_url(self):
        return self.json_config["msb_fwd"]

    def get_basic_map(self):
        return self.json_config["map_basic"]

    def get_eps(self):
        return self.json_config["eps"]

    def get_post_loc(self):
        return self.json_config["post_loc"]

    def get_post_loc_type(self):
        return self.json_config["post_loc_type"]

    def get_slo_graph(self):
        return self.json_config["slo_graph_json"]

    def get_graph_partitions(self):
        return self.json_config["graph_partitions"]