import unittest
import numpy as np
import ortools.linear_solver.pywraplp as pywraplp

def vrp(graph,D,C):
    E = []
    for row in graph:
        E.append(row + row)

    # Additional Variables
    V = np.size(C)
    # E=np.tile(graph,2)
    edges = len(E[1])
    nodes = len (E)

    # Full A MATRIX
    # CONSTRAINT IV - UPDATED - there is od number of edges on cycles
    # the right side of the equation should be zeros(n_edges*n_cycles + n_vert*n_cycles)
    # b variables = size([C])= n_cycles*n_edges + n_cycles*n_nodes

    size = 2*nodes*V + nodes*V + edges*V
    size1 = nodes * V + edges *V 
    A1 = np.zeros((size, size1))
    b1 = []
    for i in range (0, 3*nodes*V+edges*V):
        b1.append(0)
    for k in range (0, V):
        for i in range (0, nodes):
            for j in range (0, edges):
                #A1[i*V+k,j]=E[2*i*edges+k*edges+j]
                A1[k*nodes+i,j+k*edges] = E[i][j]
                A1[nodes*V+k*nodes+i,j+k*edges] = -E[i][j]
                A1[k*nodes+i,edges*V+k*nodes+i] = -2
                A1[nodes*V+k*nodes+i,edges*V+k*nodes+i] = 2
                A1[2*nodes*V+k*nodes+i,edges*V+k*nodes+i] = -1
                #A1[3*nodes*V+k*nodes+i,edges*V+k*nodes+i] = -1
    for k in range (0, V):  
        for j in range (0, edges):
            A1[3*nodes*V+k*edges+j,k*edges+j] = -1
    #print(str('\\n'.join(' '.join([str(int(val)) for val in row]) for row in A1)))

    # CONSTRAINT II - A2 - the number of packets delivered on the node is equal to all total demand on the node
    #number of rows: 2 * num. of nodes
    #number of columns: num. nodes * num. of cycles
    # variables Oki
    # B vector = [D, -D]
    b2 = D + [-val for val in D]
    for i in range (0, V*nodes):
        b2.append(0)
    sizeA2= 2*nodes + nodes*V
    sizeA21= nodes*V
    A2 = np.zeros((sizeA2, sizeA21))
    for i in range (0, nodes):
        for k in range (0, V):
                A2[i,i+nodes*k]=1
                A2[i+nodes,i+nodes*k]=-1
                A2[i*V+2*nodes+k,i*V+k]=-1

    #CONSTRAINT III A3 matrix: sum of load on each vehicles must not exceed vehicle load capacity
    # variables Oki
    sizeA3=V
    sizeA31=V*nodes
    #constants
    b3=C.copy()
    b23=b2+b3

    A3 = np.zeros((sizeA3, sizeA31))
    for k in range (0, V):                                  # for each vehicle
        for i in range (0, nodes):                         #take the sum of load on enach node (sum on Ow variables)
            #print(\"j\", j+i*V)       
            A3[k,i+k*nodes]=1
    # A23 - concatenating A2 and A3
    A23=A2
    for i in range (0, len(A3)):
        A23=np.vstack([A23, A3[i,:]])
    #print(str('\\n'.join(' '.join([str(int(val)) for val in row]) for row in A23)))

    #CONSTRAINT I - total number of all packets delivered is equal to summ of all D

    size1= 2*nodes*V + edges*V   # number of columns in matrix A1+A2+A3, variables X, K, O
    size2= V*edges*nodes         # number of additional columns in matrix A41, variables Aijk
    # b vector = d (sum of all parcels). size = 1; D_all = np.sum(D)

    # constraint 4.1. SUM for ijk -> (Eij * Aijk)
    A41 = np.zeros((1, size1+size2))
    l=0
    for i in range (0, nodes):              # itteration by node in E 
        for j in range (0, edges):         # itteration by edges in E
            for k in range (0, V):
                A41[0,(size1+l)]=-(E[i][j])
                #print(size1+l)
                l=l+1
    # Adding constraints 4.2.: Aijk - Cki*di <= 0 
    size1= V * edges * nodes   
    size2= 2*V*nodes + V*edges + V*nodes*edges
    #b vector = [0,0,...0], size = nodes* edges * V
    offsetA4=0
    A42 = np.zeros((size1, size2))
    for i in range (0, nodes):
        for j in range (0,edges): 
            for k in range (0, V):
                A42[i*edges*V+j*V+k, edges*k+j]=-D[i]
                #print(i*edges*V+j*V+k, edges*k+j)
                A42[i*edges*V+j*V+k, 2*V*nodes + V*edges + i*edges*V+j*V+k]=1
    #constraint 4.3.: Aijk - Oki <= 0
    cycles=V
    size1= cycles * edges + 2*nodes*cycles + cycles*edges*nodes   
    size= V*nodes*edges
    A43 = np.zeros((size, size1))
    #b vector = [0,0,...0], size = 

    #offset= V*nodes+V*edges
    #offset1= 2*V*nodes+V*edges
    offset=0
    offset1=edges*V+nodes*V
    offset2=edges*V+2*nodes*V
    for i in range (0, nodes):
        for j in range (0, edges):
            for k in range (0, V):       
                #print (offset+i*edges*V+j*V+k, offset1 + nodes*k+i)
                A43[offset+i*edges*V+j*V+k, offset1 + nodes*k+i]=-1
                A43[offset+i*edges*V+j*V+k,offset2+i*edges*V+j*V+k]=1           
    #concatenate A4 matrix
    A4=A41.copy()
    for i in range (0, len(A42)):
        A4=np.vstack([A4, A42[i,:]])
    for i in range (0, len(A43)):
        A4=np.vstack([A4, A43[i,:]])

    b4=[-2*np.sum(D)]
    for i in range (0, (2*V*nodes*edges)):
        b4.append(0)

    # FINAL MATRIX  - A with all constraints
    #concatenate A1 and A23 = A matrix
    A1extend = np.c_[A1, np.zeros((len(A1), len(A23[0])))]
    A23extend = np.c_[np.zeros((len(A23), len(A1[0]))), A23]

    A123=A1extend.copy()
    for i in range (0, len(A23)):
        A123=np.vstack([A123, A23extend[i,:]])

    #Final concate A123 & A4
    A123extend = np.c_[A123, np.zeros((len(A123), nodes*edges*V))]
    A=A123extend.copy()
    for i in range (0, len(A4)):
        A=np.vstack([A, A4[i,:]])
    b=b1+b23+b4
    non_zero_rows = np.count_nonzero((A != 0).sum(1)); zero_rows = len(A) - non_zero_rows
    #print (\"number of zero rows in A matirx =\", zero_rows)
    #print (\"number of variables in A =\", len(A[1]))
    #print (\"number of constraints in A =\", len(A))           

    # CREATE VARIABLES  X - vector with c11-cnn variables
    # vsak vektor v matriki X1n = dolžine len(E). 
    #Skupno število vseh vektorjev X1n = len (Et)
    #X variables X[0] to X[len(E) * V -1] -  variables in objective function 
    #K - X[len(E) * V] to X[len(E) * V + len(A1) -1]  slack variables
    #Ow - cycles load dispatch variables - X[len(E) * V + len(Et)*V*2] to X[len(E) * V + len(Et)*V*3 -1 ] 

    # C variables
    X1 = []
    for i in range (0, edges*V):
        var='x'+str(i)
        X1.append(var)

    #K variables
    K = []
    for j in range (0, V*nodes):
        #creating vector with K variables
        var='k'+str(j)
        K.append(var)

    #\"Ow\" variables
    Ow = []
    for j in range(0, V*nodes):   # numer of vehicles 
        var='Ow'+str(j)
        Ow.append(var)

    #\"Aijk\" variables
    Aijk = []
    for i in range (0,nodes):
        for j in range(0, edges):   # numer of vehicles 
            for k in range (0, V):
                var='A'+str(i)+str(j)+str(k)
                Aijk.append(var)

    #Final X vector with all variables
    X=X1.copy()
    for i in range (0,len(K)):
        X.append(K[i])
    for j in range (0,len(Ow)):
        X.append(Ow[j])
    for ijk in range (0,len(Aijk)):
        X.append(Aijk[ijk])
    print("number of all variables =", len(X))
    print("number of C variables =", len(X1))
    print("number of K variables =", len(K))
    print("number of O variables =", len(Ow))
    print("number of Aijk variables =", len(Aijk))

    #Declaring the solver
    solver = pywraplp.Solver('SolveIntegerProblem',
                               pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    x_min = -solver.infinity()                   # lower variables border 
    x_max = solver.infinity()                  # Upper variables border                        

    variables = []

    for varN, xi_name in enumerate(X1):                          # declaring objective variables [C1.... Cn]
        variables.append(solver.IntVar(0.0, x_max, xi_name))

    for varN, xi_name in enumerate(K):                          # declaring slack variables
        variables.append(solver.IntVar(0.0, x_max, xi_name))

    for varN, xi_name in enumerate(Ow):                          # declaring load doispatch variables
        variables.append(solver.NumVar(0.0, x_max, xi_name))

    for varN, xi_name in enumerate(Aijk):                          # declaring load doispatch variables
        variables.append(solver.NumVar(0.0, x_max, xi_name))

    #print('Number of variables created =', solver.NumVariables())
        #for variable in variables:
            #print('%s = %d' % (variable.name(), variable.solution_value())

        #DECLARE CONSTRAINTS
    #b = np.zeros((1, len(A)))

    for rowN, row in enumerate(A):
        left_side = None
        for colN, coeff in enumerate(row):
            if coeff == 0:
                continue
            if left_side is None:
                left_side = coeff*variables[colN]
            else:
                left_side += coeff*variables[colN]
        if left_side is None and b[rowN] < 0:
        #if left_side is None and b[0,rowN] < 0:
            raise ValueError('Constraint ' + str(rowN) + ' cannot be satisfied!')
        if left_side is not None:
            #solver.Add(left_side <= t[0,rowN])
            solver.Add(left_side <= b[rowN])

    #print('Number of constraints added =', solver.NumConstraints())

    # DECLARE OBJECTIVE FUNCTION & INVOKE THE SOLVER
    cost = None
    coeffs = [1.0 for _ in X1]
    #coeffs[3] = 100: coeffs[8] = 100: coeffs[1] = 100: coeffs[6] = 100
    for i in range (0, len(X1)):
        cost = variables[i]*coeffs[i] if i == 0 else cost + variables[i]*coeffs[i]
    solver.Minimize(cost)

    result_status = solver.Solve()
    # Check if the problem has an optimal solution.
    assert result_status == pywraplp.Solver.OPTIMAL

    objective = solver.Objective().Value()


    routes = []; Omatrix = [];
    edges_by_2 = int(edges / 2)
    for k in range (0,V):
        #print(\"cycle\", k)
        C_row = []
        for j in range (0, edges_by_2):
            #print(X[edges*k+j], variables[edges*k+j].solution_value())     
            val1 = variables[edges*k+j].solution_value()
            val2 = variables[edges*k+edges_by_2+j].solution_value()
            C_row.append(val1 + val2)
        routes.append(C_row)

    for k in range (0,V):
        O_row = []
        for i in range (0, nodes):
            O_row.append(variables[V*edges + nodes*k+i].solution_value())
        Omatrix.append(O_row)

    #return function - results
    return routes, Omatrix


class VrpTest(unittest.TestCase):

    def test1(self):
        #SIMPLE CASE
        dispatch_vec = [0, 3, 0, 4]
        capacity_vec = [4, 3]

        #network graph, stopci = povezave 12, 23, 13, vrstice = mesta
            #LJ,MB,CE,KP
        graph = [
            [1, 0, 0, 1],
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1]]

        route_mat, dispatch_mat = vrp(graph, dispatch_vec, capacity_vec)

        print("routes:")
        for row in route_mat:
            print(str(row))
        print("dispatch:")
        for row in dispatch_mat:
            print(str(row))

        assert sum(dispatch_mat[0]) == 4
        assert sum(dispatch_mat[1]) == 3

if __name__ == '__main__':
    unittest.main()
