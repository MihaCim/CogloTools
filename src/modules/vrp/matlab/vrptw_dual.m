function [beta] = vrptw_dual(P, vehicle_offsets, E, C_edge)
    % Solves the dual master problem for the
    % Vehicle Routing Problem with Time Windows
    %
    % Parameters:
    % P - the matrix of paths
    % C - a (m x k) matrix of column vectors where
    %     each column encodes the price of the edges
    %     for the k-th vehicle

    n_nodes = size(E, 1);
    n_paths = size(P, 2);
    n_vehicles = size(C_edge, 1);
    
    E_out = max(E, 0);

    % O is a (n x p) matrix the O_ip indicates
    % how many times path p leaves node i
    % Each column of O, a_j indicates how many times
    % path j leaves vertex i.
    O = E_out * P;
    
    a_rows = n_paths + n_vehicles + n_nodes + 1;
    a_cols = n_nodes + n_vehicles;
    
    A = zeros(a_rows, a_cols);
    b = zeros(a_rows, 1);
    c = zeros(a_cols, 1);
    
    eqN = 1;
    
    % INEQUALITY SET 1
    for vehicleN = 1:n_vehicles
        vehicle_offset = vehicle_offsets(vehicleN);
        
        % calculate how much each path costs for this vehicle
        path_startN = vehicle_offset;
        path_endN = vehicle_offsets(vehicleN+1) - 1;
        
        c_edge_vehicle = C_edge(vehicleN, :);
        P_vehicle = P(:, path_startN:path_endN);
        
        vehicle_path_costs = c_edge_vehicle * P_vehicle;
        
        for pathN = path_startN:path_endN
            for nodeN = 1:n_nodes
                A(eqN, nodeN) = O(nodeN, pathN);
            end
            A(eqN, n_nodes + vehicleN) = 1;
            %A(eqN, n_nodes + n_vehicles + vehicleN) = -1;
            
            b(eqN) = vehicle_path_costs(pathN - vehicle_offset + 1);
            eqN = eqN + 1;
        end
    end
    
    % INEQUALITY SET 2
    for varN = 1:a_cols
        A(eqN, varN) = -1;
        b(eqN) = 0;
        eqN = eqN + 1;
    end
    
    % INEQUALITY SET 3: DUMMY VARIABLES
    % these variables ensure that we always have a feasible solution
    A(end, 1:n_nodes) = ones(1, n_nodes);
    b(end) = 10*n_nodes*max(max(C_edge));
    
    % OBJECTIVE FUNCTION
    varN = 1;
    for nodeN = 1:n_nodes
        c(varN) = -1;
        varN = varN + 1;
    end
    
    for vehicleN = 1:n_vehicles
        c(varN) = -1;
        varN = varN + 1;
    end
    
%     for vehicleN = 1:n_vehicles
%         c(varN) = 1;
%         varN = varN + 1;
%     end 
    
    options = optimoptions('linprog','MaxIter',1000000,'Algorithm','interior-point');
    options.Display = 'off';
    beta = linprog(c, A, b, [], [], [], [], [], options);
%    options = optimoptions('linprog','MaxIter',1000000,'Algorithm', 'dual-simplex');
%    beta = linprog(c, A, b, [], [], [], [], [], options);
end