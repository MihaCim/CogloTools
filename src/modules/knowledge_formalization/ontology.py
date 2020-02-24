import subprocess
import json

class OntologyInspector:

    def __init__(self, path):
        self.path = path
        self.initOntology()
        self.edges = []

    def initOntology(self):
        """
        Transform owl ontology file to a json using robot.jar
        :return:
        """
        json_file = "ontology.json"
        try:
            cmd = '-jar robot.jar convert --input ' + self.path + " --output " + json_file
            subprocess.call('java ' + cmd, shell=True)
        except:
            print("cannot transform OWL file to JSON using robot.jar")
            return

        try:
            # TODO: Try replacing hardcoded_string with something generic, like a ontology signature (web path)
            # clear file, remove everything before # character in a file and store it in the same file (json_file)
            hardcoded_string = "http://www.semanticweb.org/angela/ontologies/2019/5/COG-LO-ontology#"
            raw_file = open(json_file, 'r')
            line_list = raw_file.readlines()
            raw_file.close()

            with open(json_file, 'w') as modified_file:
                for line in line_list:
                    new_line = line
                    if hardcoded_string in line:
                        new_line = line.replace(hardcoded_string, "")
                    modified_file.write(new_line)
            modified_file.close()
        except:
            print("cannot remove hardcoded strings from ontology in json format")
            return

        # open file as JSON
        with open(json_file) as json_file:
            data = json.load(json_file)
            graph = data["graphs"]
            content = graph[0]

            # We are only interested in edges.
            # Example: Timetable (sub) is_a PhysicalEntity (obj)
            # Example: Driver (sub) is_a HumanOperator (obj)
            # Example of JSON edge:
            #     {
            #       "sub" : "ExchangeHub",
            #       "pred" : "type",
            #       "obj" : "Station"
            #     }
            self.edges = content["edges"] #used for retrieving concept mapping

    def get_concept_mapping(self, payload):
        return []
