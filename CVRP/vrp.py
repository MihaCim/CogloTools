import unittest
import numpy as np
import ortools.linear_solver.pywraplp as pywraplp

def vrp(graph_incidence_mat, dispatch_vec, capacity_vec, start_loc_vec,Edges_length):
    
    #Data validity
    if len(start_loc_vec) != len(capacity_vec):
        raise ValueError('Number of vehicles & number of start locations not match!')
    if sum(capacity_vec) < sum(dispatch_vec):
        raise ValueError('Total vehicles capacity to low!')
    if len(graph_incidence_mat) != len(dispatch_vec):
        raise ValueError('Number of nodes in dispatch and incidence matrix dont match!')
    if len(Edges_length) != len(graph_incidence_mat[1]):
        raise ValueError('Size of edges_length and n_edges do not match!')
    E = []
    for row in graph_incidence_mat:
        E.append(row + row)

    # Additional Variables
    n_cycles = np.size(capacity_vec)
    n_edges = len(E[1])
    n_nodes = len(E)

    offset_c = 0
    offset_k = n_edges*n_cycles
    offset_o = n_cycles*n_edges + n_cycles*n_nodes
    offset_a = 2*n_nodes*n_cycles + n_edges*n_cycles   # number of columns in matrix A1+A2+A3, variables X, K, O

    # Full A MATRIX
    # CONSTRAINT IV - UPDATED - there is od number of n_edges on cycles
    # the right side of the equation should be zeros(n_edges*n_cycles + n_vert*n_cycles)
    # b variables = size([capacity_vec])= n_cycles*n_edges + n_cycles*n_nodes

    AddRow = sum(i > -1 for i in start_loc_vec)    
    rows_A1 = 2*n_nodes*n_cycles + n_nodes*n_cycles + n_edges*n_cycles + AddRow
    cols_A1 = n_nodes * n_cycles + n_edges *n_cycles

    A1 = np.zeros((rows_A1, cols_A1))
    b1 = [0 for _ in range(rows_A1-AddRow)]
    for _ in range(AddRow):
            b1.append(-1)

    offset_block0 = 0
    offset_block1 = n_nodes*n_cycles
    offset_block2 = 2*n_nodes*n_cycles
    offset_block3 = 3*n_nodes*n_cycles
    offset_block4 = 3*n_nodes*n_cycles + n_cycles*n_edges

    for k in range (n_cycles):
        for i in range (n_nodes):
            for j in range (n_edges):
                # C_kj * E_ij - 2K_ki == 0
                A1[offset_block0 + k*n_nodes + i, offset_c + k*n_edges + j] = E[i][j]
                A1[offset_block1 + k*n_nodes + i, offset_c + k*n_edges + j] = -E[i][j]
                A1[offset_block0 + k*n_nodes + i, offset_k + k*n_nodes + i] = -2
                A1[offset_block1 + k*n_nodes + i, offset_k + k*n_nodes + i] = 2
                # K_ki >= 0
                A1[offset_block2 + k*n_nodes + i, offset_k + k*n_nodes + i] = -1

    for k in range (0, n_cycles):
        for j in range (0, n_edges):
            # C_kj >= 0
            A1[offset_block3 + k*n_edges+j, offset_c + k*n_edges + j] = -1

    insert_line = 0
    for k in range (n_cycles):
        location_node = start_loc_vec[k]
        #print (location_node)
        if location_node >= 0:
            for j in range (n_edges):
                    A1[offset_block4 + insert_line, offset_c + k*n_edges+j] = -E[location_node][j]
            insert_line = insert_line+1

    # CONSTRAINT II - A2 - the number of packets delivered on the node is equal to all total demand on the node
    #number of rows: 2 * num. of n_nodes
    #number of columns: num. n_nodes * num. of cycles
    # variables Oki
    # B vector = [dispatch_vec, -dispatch_vec]
    b2 = dispatch_vec + [-val for val in dispatch_vec] + [0 for _ in range(n_cycles*n_nodes)]

    rows_A2= 2*n_nodes + n_nodes*n_cycles
    cols_A2= n_nodes*n_cycles
    A2 = np.zeros((rows_A2, cols_A2))
    for i in range (0, n_nodes):
        for k in range (0, n_cycles):
                A2[i, n_nodes*k + i]=1
                A2[i+n_nodes, n_nodes*k + i]=-1
                A2[i*n_cycles+2*n_nodes+k, i*n_cycles + k]=-1

    #CONSTRAINT III A3 matrix: sum of load on each vehicles must not exceed vehicle load capacity
    # variables Oki
    rows_A3 = n_cycles
    cols_A3 = n_cycles*n_nodes
    b3 = capacity_vec.copy()
    b23=b2+b3

    A3 = np.zeros((rows_A3 , cols_A3 ))
    for k in range (0, n_cycles):                                  # for each vehicle
        for i in range (0, n_nodes):                         #take the sum of load on enach node (sum on Ow variables)
            A3[k,i+k*n_nodes]=1
    A23=A2
    for i in range (0, len(A3)):
        A23=np.vstack([A23, A3[i,:]])
    #print(str('\\n'.join(' '.join([str(int(val)) for val in row]) for row in A23)))

    #CONSTRAINT I - total number of all packets delivered is equal to summ of all dispatch_vec
    n_vars = 2*n_nodes*n_cycles + n_edges*n_cycles   # number of columns in matrix A1+A2+A3, variables X, K, O
    n_slacks= n_cycles * n_edges * n_nodes

    cols_A4= n_vars + n_slacks

    # constraint 4.1. SUM for ijk -> (Eij * Aijk)
    A41 = np.zeros((n_nodes*n_cycles, n_vars + n_slacks))
    for k in range(n_cycles):
        for i in range(n_nodes):
            rowN = i*n_cycles + k
            A41[rowN, offset_o + k*n_nodes + i] = 2
            for j in range(n_edges):
                A41[rowN, offset_a + i*n_edges*n_cycles + j*n_cycles + k] = -E[i][j]

    # Adding constraints 4.2.: Aijk - Cki*di <= 0 
    #b vector = [0,0,...0], size = n_nodes* n_edges * n_cycles
    offsetA4=0
    A42 = np.zeros((n_slacks, cols_A4))
    for i in range (0, n_nodes):
        for j in range (0,n_edges):
            for k in range (0, n_cycles):
                A42[i*n_edges*n_cycles+j*n_cycles+k, n_edges*k+j]=-dispatch_vec[i]
                A42[i*n_edges*n_cycles+j*n_cycles+k, 2*n_cycles*n_nodes + n_cycles*n_edges + i*n_edges*n_cycles+j*n_cycles+k]=1

    #constraint 4.3.: Aijk - Oki <= 0
    A43 = np.zeros((n_slacks, cols_A4))

    offset=0
    offset1=n_edges*n_cycles+n_nodes*n_cycles
    offset2=n_edges*n_cycles+2*n_nodes*n_cycles
    for i in range (0, n_nodes):
        for j in range (0, n_edges):
            for k in range (0, n_cycles):
                #print (offset+i*n_edges*n_cycles+j*n_cycles+k, offset1 + n_nodes*k+i)
                A43[offset+i*n_edges*n_cycles+j*n_cycles+k, offset1 + n_nodes*k+i]=-1
                A43[offset+i*n_edges*n_cycles+j*n_cycles+k,offset2+i*n_edges*n_cycles+j*n_cycles+k]=1

    A4=A41.copy()
    for i in range (0, n_slacks):
        A4=np.vstack([A4, A42[i,:]])
    for i in range (0, len(A43)):
        A4=np.vstack([A4, A43[i,:]])

    b4 = [0 for _ in range(n_nodes*n_cycles)]
    # b4=[-2*np.sum(dispatch_vec)]
    for _ in range(2*n_cycles*n_nodes*n_edges):
        b4.append(0)

    #print('A4:')
    #for row in A4:
    #    print(','.join([str(val) for val in row]))
    # print('A4=\n' + str(A4))
    #print('b4=\n' + str(b4))

    # FINAL MATRIX  - A with all constraints
    #concatenate A1 and A23 = A matrix
    A1extend = np.c_[A1, np.zeros((len(A1), len(A23[0])))]
    A23extend = np.c_[np.zeros((len(A23), len(A1[0]))), A23]

    A123=A1extend.copy()
    for i in range (0, len(A23)):
        A123=np.vstack([A123, A23extend[i,:]])

    #Final concate A123 & A4
    A123extend = np.c_[A123, np.zeros((len(A123), n_nodes*n_edges*n_cycles))]
    A=A123extend.copy()
    for i in range (0, len(A4)):
        A=np.vstack([A, A4[i,:]])
    b=b1+b23+b4
    non_zero_rows = np.count_nonzero((A != 0).sum(1)); zero_rows = len(A) - non_zero_rows

    #print('A:')
    #for row in A:
    #    print(','.join([' ' + str(int(val)) for val in row]))
    # print('A4=\n' + str(A4))
    #print('b=\n' + str(b))

    # CREATE VARIABLES  X - vector with c11-cnn variables
    #X variables X[0] to X[len(E) * n_cycles -1] -  variables in objective function 
    #K - X[len(E) * n_cycles] to X[len(E) * n_cycles + len(A1) -1]  slack variables
    #Ow - cycles load dispatch variables - X[len(E) * n_cycles + len(Et)*n_cycles*2] to X[len(E) * n_cycles + len(Et)*n_cycles*3 -1 ] 

    # capacity_vec variables
    C = ['C_' + str(k) + '_' + str(j) for k in range(n_cycles) for j in range(n_edges)]
    #K variables
    K = ['K_' + str(k) + '_' + str(i) for k in range(n_cycles) for i in range(n_nodes)]
    #\"Ow\" variables
    Ow = ['O_' + str(k) + '_' + str(i) for k in range(n_cycles) for i in range(n_nodes)]

    #\"Aijk\" variables
    Aijk = []
    for i in range (n_nodes):
        for j in range(n_edges):   # numer of vehicles 
            for k in range (n_cycles):
                Aijk.append('A_' + str(i) + '_' + str(j) + '_' + str(k))

    #Final X vector with all variables
    X = C + K + Ow + Aijk

    #print("number of all variables =", len(X))
    #print("number of capacity_vec variables =", len(C))
    #print("number of K variables =", len(K))
    #print("number of O variables =", len(Ow))
    #print("number of Aijk variables =", len(Aijk))

    #Declaring the solver
    solver = pywraplp.Solver('SolveIntegerProblem',
                               pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    x_min = 0.0                   # lower variables border 
    x_max = solver.infinity()                  # Upper variables border                        

    variables = []
    for varN, xi_name in enumerate(C):                          # declaring objective variables [C1.... Cn]
        variables.append(solver.IntVar(x_min, x_max, xi_name))
    for varN, xi_name in enumerate(K):                          # declaring slack variables
        variables.append(solver.IntVar(x_min, x_max, xi_name))
    for varN, xi_name in enumerate(Ow):                          # declaring load doispatch variables
        variables.append(solver.NumVar(x_min, x_max, xi_name))
    for varN, xi_name in enumerate(Aijk):                          # declaring load doispatch variables
        variables.append(solver.NumVar(x_min, x_max, xi_name))

    #for varN, var in enumerate(variables):
    #    print('var ' + str(varN) + ': ' + str(var))

    #DECLARE CONSTRAINTS
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

    # DECLARE OBJECTIVE FUNCTION & INVOKE THE SOLVER
    #print(str(C));
    cost = None
    #coeffs = [1.0 for _ in C]
    coeffs = Edges_length + Edges_length
    #coeffs[3] = 100: coeffs[8] = 100: coeffs[1] = 100: coeffs[6] = 100
    for k in range(n_cycles):
        for coeffN in range(len(coeffs)):
            cost = variables[offset_c + k*len(coeffs) + coeffN]*coeffs[offset_c + coeffN] if coeffN == 0 else cost + variables[offset_c + k*len(coeffs) + coeffN]*coeffs[offset_c + coeffN]
            #print (variables[offset_c + k*len(coeffs) + coeffN], coeffs[offset_c + coeffN])
    # run the optimization and check if we got an optimal solution
    solver.Minimize(cost)
    result_status = solver.Solve()
    assert result_status == pywraplp.Solver.OPTIMAL

    obj_val = solver.Objective().Value()

    routes = []
    Omatrix = []

    edges_by_2 = int(0.5*n_edges)
    for k in range(n_cycles):
        C_row = []
        for j in range(edges_by_2):
            idx1 = offset_c + n_edges*k + j
            idx2 = offset_c + edges_by_2 + n_edges*k + j

            var1 = variables[idx1]
            var2 = variables[idx2]

            val1 = var1.solution_value()
            val2 = var2.solution_value()

            C_row.append(val1 + val2)
        routes.append(C_row)

    for k in range(n_cycles):
        O_row = []
        for i in range(n_nodes):
            O_row.append(variables[offset_o + n_nodes*k + i].solution_value())
        Omatrix.append(O_row)

    #return function - results
    return routes, Omatrix, obj_val
