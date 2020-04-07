from src.modules.create_graph.create_graph import JsonGraphCreator

creator = JsonGraphCreator()
use_case = "SLO-HR"
creator.create_json_graph(use_case)
