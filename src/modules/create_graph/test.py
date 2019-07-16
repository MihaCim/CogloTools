import unittest
import src.modules.create_graph.pojo.searchNode as searchNode
from src.modules.create_graph import parseOsm
import src.modules.create_graph.neighbours_finder as neighbourAlg

class TestCreateGraph(unittest.TestCase):

    def synticGraph(self):
        nodesDict = {}
        nodesDict[0] = searchNode.SearchNode(0, "A0", True)
        nodesDict[1] = searchNode.SearchNode(1, None, False)
        nodesDict[2] = searchNode.SearchNode(2, None, False)
        nodesDict[3] = searchNode.SearchNode(3, None, False)
        nodesDict[4] = searchNode.SearchNode(4, None, False)
        nodesDict[5] = searchNode.SearchNode(5, None, False)
        nodesDict[6] = searchNode.SearchNode(6, None, False)
        nodesDict[7] = searchNode.SearchNode(7, "A1", True)
        nodesDict[8] = searchNode.SearchNode(8, None, False)
        nodesDict[9] = searchNode.SearchNode(9, None, False)
        nodesDict[10] = searchNode.SearchNode(10, None, False)
        nodesDict[11] = searchNode.SearchNode(11, "A2", True)
        nodesDict[12] = searchNode.SearchNode(12, "A3", True)
        nodesDict[13] = searchNode.SearchNode(13, "A4", True)
        nodesDict[14] = searchNode.SearchNode(14, None, False)
        nodesDict[15] = searchNode.SearchNode(15, None, False)
        nodesDict[16] = searchNode.SearchNode(16, None, False)
        nodesDict[17] = searchNode.SearchNode(17, None, False)
        nodesDict[18] = searchNode.SearchNode(18, None, False)
        nodesDict[19] = searchNode.SearchNode(19, "A5", True)
        nodesDict[20] = searchNode.SearchNode(20, None, False)
        nodesDict[21] = searchNode.SearchNode(21, None, False)
        nodesDict[22] = searchNode.SearchNode(22, None, False)
        nodesDict[24] = searchNode.SearchNode(24, None, False)
        nodesDict[23] = searchNode.SearchNode(23, None, False)
        nodesDict[25] = searchNode.SearchNode(25, "A6", True)
        nodesDict[26] = searchNode.SearchNode(26, None, False)
        nodesDict[27] = searchNode.SearchNode(27, "A7", True)
        nodesDict[28] = searchNode.SearchNode(28, None, False)
        nodesDict[29] = searchNode.SearchNode(29, None, False)
        nodesDict[30] = searchNode.SearchNode(30, None, False)
        nodesDict[31] = searchNode.SearchNode(31, None, False)
        nodesDict[32] = searchNode.SearchNode(32, None, False)
        nodesDict[33] = searchNode.SearchNode(33, None, False)
        nodesDict[34] = searchNode.SearchNode(34, "A8", True)
        nodesDict[35] = searchNode.SearchNode(35, None, False)
        nodesDict[36] = searchNode.SearchNode(36, None, False)
        nodesDict[37] = searchNode.SearchNode(37, None, False)
        nodesDict[38] = searchNode.SearchNode(38, None, False)
        nodesDict[39] = searchNode.SearchNode(39, None, False)
        nodesDict[40] = searchNode.SearchNode(40, "A9", True)
        nodesDict[41] = searchNode.SearchNode(41, "A10", True)
        nodesDict[42] = searchNode.SearchNode(42, None, False)
        nodesDict[43] = searchNode.SearchNode(43, None, False)
        nodesDict[44] = searchNode.SearchNode(44, None, False)
        nodesDict[45] = searchNode.SearchNode(45, None, False)
        nodesDict[46] = searchNode.SearchNode(46, None, False)

        edgesDict = {
            0: {1: {'weight': 2}, 2: {'weight': 2}, 3: {'weight': 2}, 4: {'weight': 2}},
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
            46: {45: {'weight': 0.5}}
        }

        return nodesDict, edgesDict

    def test_complex_graph(self):
        nodesDict, edgesDict = self.synticGraph()

        finder = neighbourAlg.NeighboursFinder()

        result =finder.search_near_posts(nodesDict, edgesDict, 0, 1)

        self.assertLessEqual(result, ['A8', 'A5', 'A7', 'A10', 'A1'])



