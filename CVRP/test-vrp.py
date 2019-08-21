#!/bin/bash

#python3 vrp.py

from vrp import vrp
import unittest


class TestSum(unittest.TestCase):
    def test_1(self):
        # read file test-vrp
        dispatch_vec = [0, 3, 0, 4]
        capacity_vec = [4, 3]


        #network graph, stopci = povezave 12, 23, 13, vrstice = mesta
        #LJ,MB,CE,KP
        graph = [
                [1, 0, 0, 1],
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 1]
        ]

        route_mat, dispatch_mat, obj_val = vrp(graph, dispatch_vec, capacity_vec)

        print('obj val: ' + str(obj_val))
        print("routes:")
        for row in route_mat:
            print(str(row))
        print("dispatch:")
        for row in dispatch_mat:
            print(str(row))
        assert obj_val == 4
        assert sum(route_mat[0]) == 2
        assert sum(route_mat[1]) == 2
        assert sum(dispatch_mat[0]) == 4
        assert sum(dispatch_mat[1]) == 3
        print("test #1 finnished")

    def test_2(self):
        # read file test-vrp
        dispatch_vec = [11, 22, 33, 44, 55, 66]
        capacity_vec = [300]


        #network graph, stopci = povezave 12, 23, 13, vrstice = mesta
        #LJ,MB,CE,KP
        graph = [
            [1, 0, 0, 0, 0, 1, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 1, 1],
            [0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 1, 0, 0, 0]
        ]

        route_mat, dispatch_mat, obj_val = vrp(graph, dispatch_vec, capacity_vec)

        print('obj val: ' + str(obj_val))
        print("routes:")
        for row in route_mat:
            print(str(row))
        print("dispatch:")
        for row in dispatch_mat:
            print(str(row))
        #assert obj_val == 4
        #assert sum(route_mat[0]) == 3
        #assert sum(route_mat[1]) == 2
        #assert sum(dispatch_mat[0]) == 4
        #assert sum(dispatch_mat[1]) == 3
        print(obj_val)
        print(route_mat[0])
        #print(route_mat[1])
        print(dispatch_mat[0])
        #print(dispatch_mat[1])
        print("test #2 finnished")


    def test_3(self):
        # read file test-vrp
        dispatch_vec = [11, 22, 33, 44, 55, 66]
        capacity_vec = [80, 80, 80]
        #network graph, stopci = povezave 12, 23, 13, vrstice = mesta
        #LJ,MB,CE,KP
        graph = [
            [1, 0, 0, 0, 0, 1, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 1, 1],
            [0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 1, 0, 0, 0]
        ]

        route_mat, dispatch_mat, obj_val = vrp(graph, dispatch_vec, capacity_vec)

        print('obj val: ' + str(obj_val))
        print("routes:")
        for row in route_mat:
            print(str(row))
        print("dispatch:")
        for row in dispatch_mat:
            print(str(row))
        #assert obj_val == 4
        #assert sum(route_mat[0]) == 3
        #assert sum(route_mat[1]) == 2
        #assert sum(dispatch_mat[0]) == 4
        #assert sum(dispatch_mat[1]) == 3
        print(obj_val)
        print(route_mat[0])
        print(route_mat[1])
        print(dispatch_mat[0])
        print(dispatch_mat[1])
        print("test #3 finnished")


if __name__ == '__main__':
    unittest.main()
