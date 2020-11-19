from jsonschema import validate
import json


class ErrorHandling:

    @staticmethod
    def check_messages_correction(input_data):
        event = input_data['event']['event']
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