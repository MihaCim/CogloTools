
import json


class ConfigParser:

    def __init__(self):
        config_path = './modules/create_graph/config/config.json'
        with open(config_path) as config:
            self.json_config = json.load(config)
        config.close()

    def get_pickle_path(self, use_case):
        if use_case == "SLO-HR":
            return self.json_config["slo_hr_pickle_path"]
        else:
            return self.json_config["elta_pickle_path"]

    def get_graph_path(self, use_case):
        if use_case == "SLO-HR":
            return self.json_config["slo_hr_json_graph_data_path"]
        else:
            return self.json_config["elta_json_graph_data_path"]

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