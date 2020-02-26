function [y, cost] = vrptw_primal(P, vehicle_offset_v, E, C_edge)
    % Vehicle routing with time windows master problem.
    % 
    % Selects an optimal path from the set of paths in the column
    % vector P. Each column in P is a binary vector x that describes
    % which edges are in the path.
    %
    % E is the directed incidence matrix of the graph.
    % 
    % Parameters:
    % P - the matrix of column vectors that represent paths
    % E - directed incidence matrix
    % C_edge - matrix of column vectors that encode the price of each edge
    % for vehicle k
    
    n_nodes = size(E, 1);
    n_paths = size(P, 2);
    n_vehicles = size(C_edge, 1);
    
    E_out = max(E, 0);
    
    % O is a (n x p) matrix the O_ik indicates
    % how many times path k leaves node i
    % Each column of O, a_j indicates how many times
    % path j leaves vertex i.
    O = E_out * P;
     
    A_rows = n_nodes + 2*n_vehicles + n_paths;
    A_cols = n_paths;
    
    % structures used by the linear program
    A = zeros(A_rows, A_cols);
    b = zeros(A_rows, 1);
    c = zeros(n_paths, 1);
    
    % inequality set 1
    % each customer should be visited at least once
    eqN = 1;
    for nodeN = 1:n_nodes
        for vehicleN = 1:n_vehicles
            startN = vehicle_offset_v(vehicleN);
            endN = vehicle_offset_v(vehicleN+1) - 1;
            
            for pathN = startN:endN
                A(eqN, pathN) = -O(nodeN, pathN);
            end
        end
        b(eqN) = -1;
        eqN = eqN + 1;
    end
    
    % inequality set 2
    % sum_y_j >= 1
    for vehicleN = 1:n_vehicles
        startN = vehicle_offset_v(vehicleN);
        endN = vehicle_offset_v(vehicleN+1) - 1;
        
        for pathN = startN:endN
            A(eqN, pathN) = -1;
        end
        b(eqN) = -1;
        eqN = eqN + 1;
    end
    % sum_y_j <= 1
    % XXX: These were added even though in theory they should not
    % XXX: be required!
    % XXX: Check why the procedure sometimes fails without them.
    for vehicleN = 1:n_vehicles
        startN = vehicle_offset_v(vehicleN);
        endN = vehicle_offset_v(vehicleN+1) - 1;
        
        for pathN = startN:endN
            A(eqN, pathN) = 1;
        end
        b(eqN) = 1;
        eqN = eqN + 1;
    end
    
    % inequality set 3
    % y_j >= 0
    for pathN = 1:n_paths
        A(eqN, pathN) = -1;
        b(eqN) = 0;
        eqN = eqN + 1;
    end
    
    % construct the objective function
    % find the cost of an empty path
    min_cost = inf;
    for vehicleN = 1:n_vehicles
        startN = vehicle_offset_v(vehicleN);
        endN = vehicle_offset_v(vehicleN+1) - 1;
        
        edge_costs = C_edge(vehicleN, :);
        P_vehicle = P(:, startN:endN);
        
        c_vehicle = edge_costs * P_vehicle;
        min_vehicle_cost = min(c_vehicle(c_vehicle > 0))*1e-2; % all paths must have at least some minimal cost
        
        if min_vehicle_cost < min_cost
            min_cost = min_vehicle_cost;
        end
    end
    
    empty_cost = min_cost * 1e-4;
    for vehicleN = 1:n_vehicles
        startN = vehicle_offset_v(vehicleN);
        endN = vehicle_offset_v(vehicleN+1) - 1;
        
        edge_costs = C_edge(vehicleN, :);
        P_vehicle = P(:, startN:endN);
        
        c_vehicle = edge_costs * P_vehicle;
        c(startN:endN) = max(empty_cost, c_vehicle);
    end
    
    % find the solution
    options = optimoptions('linprog','MaxIter',100000,'Algorithm', 'dual-simplex');
    options.Display = 'off';
    y = linprog(c, A, b, [], [], [], [], [], options);
    
    if size(y, 1) == 0
        cost = inf;
    else 
        cost = c'*y;
    end
end