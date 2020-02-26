class GraphPrune:

    def PruneG (self, data):

            new_data = {}
            new_data['nodes'] = data['nodes']
            new_data['edge'] = {}

            new_list = []
            check_dict = {}
            for edge in data['edge']:
                if edge[0] not in check_dict:
                    check_dict[edge[0]] = {edge[1]: edge[2]}
                elif edge[0] in check_dict and edge[1] not in check_dict[edge[0]]:
                    check_dict[edge[0]][edge[1]] = edge[2]
                elif edge[0] in check_dict and edge[1] in check_dict[edge[0]]:
                    if check_dict[edge[0]][edge[1]] > edge[2]:
                        check_dict[edge[0]][edge[1]] = edge[2]

            for key, d in check_dict.items():
                for key2, dist in d.items():
                    new_list.append([key, key2, dist])

            new_data['edge'] = new_list
            return new_data
