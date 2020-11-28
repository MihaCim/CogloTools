from jsonschema import validate
import json

from src.modules.create_graph.config import config_parser


class ErrorHandling:
    slo_case = {'SLO', 'PS'}

    def check_organization(self, input_data):
        '''
         Organization ce je slo-cro/ ps hp
        '''

        if input_data['organization'] == 'ELTA':
            for item in input_data['event']['info']['item']:
                if item['organization'] != 'ELTA':
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

            for clo in input_data['clos']:
                if clo['info']['organization'] != 'ELTA':
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

            for parcel in input_data['parcels']:
                if parcel['organization'] != 'ELTA':
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

        if input_data['organization'] == 'PS':
            for item in input_data['event']['info']['item']:
                if item['organization'] not in self.slo_case:
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

            for clo in input_data['clos']:
                if clo['info']['organization'] not in self.slo_case:
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

            for parcel in input_data['parcels']:
                if parcel['organization'] not in self.slo_case:
                    raise ValueError("Wrong organization. Organization should be the same at the same message")

    def check_complited_plan(self, input_data):
        '''
         daily plan -> complited plan prazn oz missing
        '''

        for clo in input_data['clos']:
            if 'completed_plan' not in clo['state']:
                raise ValueError("Completed plan is missing")

    def check_locations(self, input_data):

        if input_data['organization'] == "PS" or \
           input_data['organization'] == "HP" :
            use_case_graph = config_parser.ConfigParser()
            use_case_graph.get_graph_path("SLO-CRO_urban")
            f = open(config_parser.get_graph_path(use_case_graph), "r")
            print(f)

        if input_data['organization'] == "SLO-CRO":
            pass

    def check_messages_correction(self, input_data):
        event = input_data['event']['event_type']
        '''
        organization = input_data['organization']
        if event == 'breakdown' or organization == 'SLO-CRO':
            f = open('./modules/demo/schemas/PS_HP_brokenvehicle.json', )
            json_schema = json.load(f)
            validate(instance=input_data, schema=json_schema)
        elif event == 'order' and (organization == 'PS' or organization == 'HP'):
            f = open('./modules/demo/schemas/PS_HP_ad-hoc.json', )
            json_schema = json.load(f)
            validate(instance=input_data, schema=json_schema)
        elif event == 'order' and organization == 'ELTA':
            f = open('./modules/demo/schemas/Elta_ad-hoc.json', )
            json_schema = json.load(f)
            validate(instance=input_data, schema=json_schema)
        #TODO missing daily_plan
        '''
        #1.) Check the organization
        self.check_organization(input_data)

        self.check_complited_plan(input_data)

        self.check_locations(input_data)


        # 3.) slo cro use case vsi locaisni (pri vsakem parslu in pri vsaki cloju)
        # v fajlu grapf/data poklice z configa
        # get_csv_path(self, use_case):
        #         if use_case == "SLO-CRO_crossborder":

        # 4.) event type precekiraj:
        '''
                            if type == "order":
                        type = "AdHocRequest"
                    elif type == "vehicle":
                        type = "brokenVehicle"
                    elif type == "border":
                    
                    none je pri daily planu 
                                    if "event" not in json:
        '''

        # vsi:
        # 5.)         parcels -> payweight == 1 :)
        # 6.) id od parclov/clo so unique znotrej celga message
        # clos: parcels: lahko prazen [] ali pa se kej dodati gor -vsi
        # ce ima parsel v planu jih mora imeti tudi tokaj zlisatne
