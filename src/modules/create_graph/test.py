import unittest
import modules.create_graph.pojo.search_node as search_node
import modules.create_graph.neighbours_finder as neighbour_alg

class TestCreateGraph(unittest.TestCase):

    def syntetic_graph1_construction(self):
        nodes = {}
        nodes[0] = search_node.SearchNode(0, 'A0', True)
        nodes[1] = search_node.SearchNode(1, None, False)
        nodes[2] = search_node.SearchNode(2, None, False)
        nodes[3] = search_node.SearchNode(3, None, False)
        nodes[4] = search_node.SearchNode(4, None, False)
        nodes[5] = search_node.SearchNode(5, None, False)
        nodes[6] = search_node.SearchNode(6, 'A1', True)
        nodes[7] = search_node.SearchNode(7, 'A2', True)
        nodes[8] = search_node.SearchNode(8, None, False)
        nodes[9] = search_node.SearchNode(9, None, False)
        nodes[10] = search_node.SearchNode(10, None, False)
        nodes[11] = search_node.SearchNode(11, None, False)
        nodes[12] = search_node.SearchNode(12, 'A3', True)
        nodes[13] = search_node.SearchNode(13, None, False)
        nodes[14] = search_node.SearchNode(14, 'A4', True)
        nodes[15] = search_node.SearchNode(15, None, False)
        nodes[16] = search_node.SearchNode(16, None, False)
        nodes[17] = search_node.SearchNode(17, None, False)
        nodes[18] = search_node.SearchNode(18, None, False)
        nodes[19] = search_node.SearchNode(19, None, False)
        nodes[20] = search_node.SearchNode(20, None, False)
        nodes[21] = search_node.SearchNode(21, None, False)
        nodes[22] = search_node.SearchNode(22, None, False)
        nodes[23] = search_node.SearchNode(23, 'A5', True)
        nodes[24] = search_node.SearchNode(24, None, False)
        nodes[25] = search_node.SearchNode(25, None, False)
        nodes[26] = search_node.SearchNode(26, None, False)
        nodes[27] = search_node.SearchNode(27, None, False)
        nodes[28] = search_node.SearchNode(28, None, False)
        nodes[29] = search_node.SearchNode(29, None, False)
        nodes[30] = search_node.SearchNode(30, None, False)

        edges = {0: {1: {"weight": 0.5}, 2: {"weight": 0.2}, 20: {"weight": 0.3}, 21: {"weight": 0.6}},
                 1: {7: {"weight": 0.5}, 0: {"weight": 0.5}},
                 2: {0: {"weight": 0.5}, 3: {"weight": 0.5}, 6: {"weight": 0.5}},
                 3: {2: {"weight": 0.5}, 4: {"weight": 0.5}, 5: {"weight": 0.5}},
                 4: {3: {"weight": 0.5}},
                 5: {3: {"weight": 0.5}},
                 6: {2: {"weight": 0.5}, 7: {"weight": 0.5}, 16: {"weight": 0.5}},
                 7: {8: {"weight": 0.5}, 11: {"weight": 0.5}, 15: {"weight": 0.5}, 6: {"weight": 0.5},
                     1: {"weight": 0.5}},
                 8: {9: {"weight": 0.5}, 10: {"weight": 0.5}, 7: {"weight": 0.5}},
                 9: {8: {"weight": 0.5}},
                 10: {11: {"weight": 0.5}, 8: {"weight": 0.5}},
                 11: {10: {"weight": 0.5}, 7: {"weight": 0.5}},
                 12: {15: {"weight": 0.5}},
                 13: {15: {"weight": 0.5}},
                 14: {16: {"weight": 0.5}},
                 15: {13: {"weight": 0.5}, 12: {"weight": 0.5}, 7: {"weight": 0.5}, 16: {"weight": 0.5}},
                 16: {14: {"weight": 0.5}, 15: {"weight": 0.5}, 6: {"weight": 0.5}},
                 17: {19: {"weight": 0.5}},
                 18: {19: {"weight": 0.5}},
                 19: {17: {"weight": 0.5}, 18: {"weight": 0.5}, 20: {"weight": 0.5}},
                 20: {19: {"weight": 0.5}, 0: {"weight": 0.5}, 23: {"weight": 0.5}},
                 21: {0: {"weight": 0.5}, 24: {"weight": 0.5}, 25: {"weight": 0.5}},
                 22: {23: {"weight": 0.5}},
                 23: {20: {"weight": 0.5}, 22: {"weight": 0.5}, 26: {"weight": 0.5}},
                 24: {21: {"weight": 0.5}, 27: {"weight": 0.5}, 28: {"weight": 0.5}, 29: {"weight": 0.5}},
                 25: {21: {"weight": 0.5}, 30: {"weight": 0.5}, 29: {"weight": 0.5}},
                 26: {23: {"weight": 0.5}},
                 27: {24: {"weight": 0.5}},
                 28: {24: {"weight": 0.5}},
                 29: {24: {"weight": 0.5}, 25: {"weight": 0.5}},
                 30: {25: {"weight": 0.5}}}

        return nodes, edges

    def syntic_graph2_constraction(self):
        nodes_dict = {}
        nodes_dict[0] = search_node.SearchNode(0, "A0", True)
        nodes_dict[1] = search_node.SearchNode(1, None, False)
        nodes_dict[2] = search_node.SearchNode(2, None, False)
        nodes_dict[3] = search_node.SearchNode(3, None, False)
        nodes_dict[4] = search_node.SearchNode(4, None, False)
        nodes_dict[5] = search_node.SearchNode(5, None, False)
        nodes_dict[6] = search_node.SearchNode(6, None, False)
        nodes_dict[7] = search_node.SearchNode(7, "A1", True)
        nodes_dict[8] = search_node.SearchNode(8, None, False)
        nodes_dict[9] = search_node.SearchNode(9, None, False)
        nodes_dict[10] = search_node.SearchNode(10, None, False)
        nodes_dict[11] = search_node.SearchNode(11, "A2", True)
        nodes_dict[12] = search_node.SearchNode(12, "A3", True)
        nodes_dict[13] = search_node.SearchNode(13, "A4", True)
        nodes_dict[14] = search_node.SearchNode(14, None, False)
        nodes_dict[15] = search_node.SearchNode(15, None, False)
        nodes_dict[16] = search_node.SearchNode(16, None, False)
        nodes_dict[17] = search_node.SearchNode(17, None, False)
        nodes_dict[18] = search_node.SearchNode(18, None, False)
        nodes_dict[19] = search_node.SearchNode(19, "A5", True)
        nodes_dict[20] = search_node.SearchNode(20, None, False)
        nodes_dict[21] = search_node.SearchNode(21, None, False)
        nodes_dict[22] = search_node.SearchNode(22, None, False)
        nodes_dict[24] = search_node.SearchNode(24, None, False)
        nodes_dict[23] = search_node.SearchNode(23, None, False)
        nodes_dict[25] = search_node.SearchNode(25, "A6", True)
        nodes_dict[26] = search_node.SearchNode(26, None, False)
        nodes_dict[27] = search_node.SearchNode(27, "A7", True)
        nodes_dict[28] = search_node.SearchNode(28, None, False)
        nodes_dict[29] = search_node.SearchNode(29, None, False)
        nodes_dict[30] = search_node.SearchNode(30, None, False)
        nodes_dict[31] = search_node.SearchNode(31, None, False)
        nodes_dict[32] = search_node.SearchNode(32, None, False)
        nodes_dict[33] = search_node.SearchNode(33, None, False)
        nodes_dict[34] = search_node.SearchNode(34, "A8", True)
        nodes_dict[35] = search_node.SearchNode(35, None, False)
        nodes_dict[36] = search_node.SearchNode(36, None, False)
        nodes_dict[37] = search_node.SearchNode(37, None, False)
        nodes_dict[38] = search_node.SearchNode(38, None, False)
        nodes_dict[39] = search_node.SearchNode(39, None, False)
        nodes_dict[40] = search_node.SearchNode(40, "A9", True)
        nodes_dict[41] = search_node.SearchNode(41, "A10", True)
        nodes_dict[42] = search_node.SearchNode(42, None, False)
        nodes_dict[43] = search_node.SearchNode(43, None, False)
        nodes_dict[44] = search_node.SearchNode(44, None, False)
        nodes_dict[45] = search_node.SearchNode(45, None, False)
        nodes_dict[46] = search_node.SearchNode(46, None, False)
        nodes_dict[47] = search_node.SearchNode(47, None, False)
        nodes_dict[48] = search_node.SearchNode(48, None, False)
        nodes_dict[49] = search_node.SearchNode(49, None, False)
        nodes_dict[50] = search_node.SearchNode(50, None, False)
        nodes_dict[51] = search_node.SearchNode(51, "A11", True)
        nodes_dict[52] = search_node.SearchNode(52, None, False)
        nodes_dict[53] = search_node.SearchNode(53, None, False)
        nodes_dict[54] = search_node.SearchNode(54, None, False)
        nodes_dict[55] = search_node.SearchNode(55, None, False)
        nodes_dict[56] = search_node.SearchNode(56, None, False)
        nodes_dict[57] = search_node.SearchNode(57, "A12", True)

        edges_dict = {
            0: {1: {'weight': 2}, 2: {'weight': 2}, 3: {'weight': 2}, 4: {'weight': 2}, 47: {'weight': 3.5}},
            1: {5: {'weight': 0.5}, 6: {'weight': 2}, 0: {'weight': 2}},
            2: {0: {'weight': 2}, 9: {'weight': 2}, 10: {'weight': 6}},
            3: {0: {'weight': 2}, 19: {'weight': 2}, 20: {'weight': 2}},
            4: {0: {'weight': 2}, 30: {'weight': 0.5}},
            5: {1: {'weight': 0.5}},
            6: {1: {'weight': 2}, 7: {'weight': 2}, 8: {'weight': 1.5}},
            7: {6: {'weight': 2}},
            8: {6: {'weight': 1.5}, 42: {'weight': 2}},
            9: {41: {'weight': 0.5}, 12: {'weight': 2}, 2: {'weight': 2}, 13: {'weight': 0.7}},
            10: {2: {'weight': 6}, 11: {'weight': 2}},
            11: {10: {'weight': 2}, 45: {'weight': 2}},
            12: {9: {'weight': 1.5}},
            13: {9: {'weight': 0.7}, 14: {'weight': 0.5}, 15: {'weight': 0.5}},
            14: {13: {'weight': 0.5}},
            15: {13: {'weight': 0.5}},
            16: {41: {'weight': 0.5}, 17: {'weight': 0.5}},
            17: {16: {'weight': 0.5}, 18: {'weight': 0.5}, 44: {'weight': 0.5}},
            18: {17: {'weight': 0.5}},
            19: {3: {'weight': 2}, 45: {'weight': 0.5}},
            20: {3: {'weight': 2}, 21: {'weight': 0.3}, 27: {'weight': 0.3}},
            21: {20: {'weight': 0.5}, 25: {'weight': 0.3}, 22: {'weight': 0.3}},
            22: {21: {'weight': 0.5}, 24: {'weight': 0.3}, 23: {'weight': 0.3}},
            23: {22: {'weight': 0.5}},
            24: {22: {'weight': 0.5}},
            25: {21: {'weight': 0.5}, 26: {'weight': 0.3}},
            26: {25: {'weight': 0.5}},
            27: {20: {'weight': 0.5}, 28: {'weight': 0.3}, 29: {'weight': 0.3}},
            28: {27: {'weight': 0.65}},
            29: {27: {'weight': 0.65}},
            30: {4: {'weight': 0.5}, 31: {'weight': 0.3}, 32: {'weight': 0.3}, 37: {'weight': 0.3}},
            31: {30: {'weight': 0.5}},
            32: {30: {'weight': 0.3}, 33: {'weight': 0.3}, 34: {'weight': 0.3}},
            33: {32: {'weight': 0.4}},
            34: {35: {'weight': 0.5}, 32: {'weight': 0.3}},
            35: {34: {'weight': 0.5}, 36: {'weight': 0.3}},
            36: {35: {'weight': 0.5}},

            37: {30: {'weight': 0.5}, 38: {'weight': 0.3}},
            38: {37: {'weight': 0.5}, 39: {'weight': 0.3}},
            39: {38: {'weight': 0.5}, 40: {'weight': 3}},
            40: {39: {'weight': 5}},
            41: {9: {'weight': 0.5}, 16: {'weight': 0.5}, 42: {'weight': 0.5}},
            42: {8: {'weight': 0.5}, 41: {'weight': 0.5}, 43: {'weight': 0.5}},
            43: {42: {'weight': 0.5}},
            44: {17: {'weight': 0.5}},
            45: {11: {'weight': 0.5}, 19: {'weight': 0.5}, 46: {'weight': 0.15}},
            46: {45: {'weight': 0.5}},
            47: {0: {'weight': 3.5}, 48: {'weight': 0.45}, 55: {'weight': 0.45}},
            48: {47: {'weight': 0.45}, 49: {'weight': 0.45}},
            49: {48: {'weight': 0.45}, 51: {'weight': 0.45}, 50: {'weight': 0.45}},
            50: {49: {'weight': 0.45}},
            51: {49: {'weight': 0.45}, 52: {'weight': 0.45}},
            52: {51: {'weight': 0.45}, 53: {'weight': 0.45}, 56: {'weight': 0.45}},
            53: {52: {'weight': 0.45}, 54: {'weight': 0.45}},
            54: {53: {'weight': 0.45}, 55: {'weight': 0.45}},
            55: {54: {'weight': 0.45}, 47: {'weight': 0.45}},
            56: {52: {'weight': 0.45}},
            57: {56: {'weight': 0.45}}
        }

        return nodes_dict, edges_dict

    def test_simple_graph(self):
        nodes_dict, edges_dict = self.syntetic_graph1_construction()

        finder = neighbour_alg.NeighboursFinder()
        result =finder.search_near_posts(nodes_dict, edges_dict, 0, 1)

        print(result)
        self.assertLessEqual(result, ['A2', 'A5', 'A1'])


    def test_complex_graph(self):
        nodes_dict, edges_dict = self.syntic_graph2_constraction()

        finder = neighbour_alg.NeighboursFinder()
        result =finder.search_near_posts(nodes_dict, edges_dict, 0, 1)

        self.assertLessEqual(result, ['A8', 'A5', 'A7', 'A10', 'A11', 'A1'])



