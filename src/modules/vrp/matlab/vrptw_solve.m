function [R_out, cost] = vrptw_solve(E_raw, C_raw, t_vec, start_v, end_v, distr_vec, capacity_vec, t_start_vec, t_end_vec)
    % Solves the vehicle routing problem with
    % time windows.
    %
    % Notation:
    % n - number of nodes
    % m - number of edges
    % k - number of vehicles
    %
    % Parameters:
    % E - the incidence matrix that determines the graph
    % C - a (k x m) matrix
    % time_vec - a vector of dimension m of travel times
    % start_v - a vector of length k of start locations
    % end_v - a vector of length k of end locations
    % distr_vec - a vector of length n with values indicating how much
    %             should be dropped off at each node 
    % capacity_vec - a vector that stores the capacity of each vehicle
    % t_start_vec - a vector of start times for each node
    % t_end_vec - a vector of end times for each node
    
    tic
    
    % first generate a clique from the given graph
    [E, C, T, E2E_raw] = get_clique(E_raw, C_raw, t_vec);
    
    eps = 1e-7;
    
    n_nodes = size(E, 1);
    n_edges = size(E, 2);
    n_vehicles = size(C, 1);
    
    branch_queue = java.util.ArrayList();
    branch_queue.add(zeros(n_vehicles*n_edges, 2));
    
    edgeN2srcN = @(edgeN) ceil(edgeN / (n_nodes - 1));
    function [d] = edgeN2dstN(edgeN)
        srcN = edgeN2srcN(edgeN);
        
        offset = mod(edgeN, n_nodes-1);
        if offset == 0
            offset = n_nodes-1;
        end
        
        if offset >= srcN
            d = offset + 1;
        else
            d = offset;
        end
    end
    function [edgeN] = nodeN2edgeN(srcN, dstN, n_nodes)
        offset_dst = dstN;
        if dstN > srcN
            offset_dst = dstN-1;
        end

        edgeN = (srcN-1)*(n_nodes-1) + offset_dst;
    end

    best_cost = inf;
    best_path_wgt_v = [];
    best_P = [];
    best_vehicle_offset_v = [];

    iterN = 0;
    
    while ~branch_queue.isEmpty()
        total_tasks = branch_queue.size();
        
        iterN = iterN + 1;
        if mod(iterN, 1) == 0
            disp(['Branch-and-Bound iteration: ', num2str(iterN), ' number of pending tasks: ', num2str(total_tasks)]);
        end
        
        edge_branch_blacklist_mat = branch_queue.remove(0);
        edge_blacklist_vec = edge_branch_blacklist_mat(:, 1);
        edge_branch_vec = edge_branch_blacklist_mat(:, 2);
        
        %======================================
        disp('============================================');
        for vehicleN = 1:n_vehicles
            startN = (vehicleN-1)*n_edges + 1;
            endN = vehicleN*n_edges;
            vehicle_branch_vec = edge_branch_vec(startN:endN);
            include_idxs = find(vehicle_branch_vec > 0);
            exclude_idxs = find(vehicle_branch_vec < 0);
            
            disp(['VEHICLE ', num2str(vehicleN)]);
            disp('included edges');
            for valN = 1:length(include_idxs)
                edgeN = include_idxs(valN);
                srcN = edgeN2srcN(edgeN);
                dstN = edgeN2dstN(edgeN);
                disp([num2str(srcN), ' -> ', num2str(dstN)]);
            end
            disp('excluded edges');
            for valN = 1:length(exclude_idxs)
                edgeN = exclude_idxs(valN);
                srcN = edgeN2srcN(edgeN);
                dstN = edgeN2dstN(edgeN);
                disp([num2str(srcN), ' -> ', num2str(dstN)]);
            end
        end
        %======================================
            
        %disp('edge blacklist');
        %edge_blacklist_vec'
        [path_wgt_v, cost, P, vehicle_offset_v] = vrptw_solve_bnb( ...
            E, ...
            C, ...
            T, ...
            start_v, ...
            end_v, ...
            distr_vec, ...
            capacity_vec, ...
            t_start_vec, ...
            t_end_vec, ...
            eps, ...
            edge_blacklist_vec ...
        );
        %disp('path vgt vec');
        %path_wgt_v'
    
        if size(path_wgt_v, 1) == 0
            disp('did not find a solution');
            continue;
        end
        
        % find the edges on which the vehicles go probabilistically
        rational_idxs = [];
        
        for vehicleN = n_vehicles:-1:1
            startN = vehicle_offset_v(vehicleN);
            endN = vehicle_offset_v(vehicleN+1)-1;
            
            P_vehicle = P(:, startN:endN);
            vehicle_path_wgt_v = path_wgt_v(startN:endN);
            
            edge_wgt_vec = P_vehicle*vehicle_path_wgt_v;
        
            rational_idxs = (vehicleN-1)*n_edges + find(eps < edge_wgt_vec & edge_wgt_vec < 1 - eps, 1);
            
            if ~isempty(rational_idxs)
                disp(['vehicle ', num2str(vehicleN), ' edge weights: ', num2str(edge_wgt_vec.')]);
                break;
            end
        end
        
        if isempty(rational_idxs)
            if cost < best_cost
                best_cost = cost;
                best_path_wgt_v = path_wgt_v;
                best_P = P;
                best_vehicle_offset_v = vehicle_offset_v;
                disp(['found a new best solution, cost: ', num2str(cost)]);
            else
                disp(['found a new solution, cost: ', num2str(cost)]);
            end
            continue;
        end
        
        % branch
        branch_vehicle_edgeN = rational_idxs(1);
        branch_vehicleN = ceil(branch_vehicle_edgeN / n_edges);
        branch_edgeN = mod(branch_vehicle_edgeN, n_edges);
        srcN = edgeN2srcN(branch_edgeN);
        dstN = edgeN2dstN(branch_edgeN);
        
        if edge_branch_vec(branch_vehicle_edgeN) ~= 0
            continue;
        end
        
        disp(['found rational solution, branching on vehicle ', num2str(branch_vehicleN), ' edge: ', num2str(srcN),' -> ', num2str(dstN), ' (', num2str(branch_edgeN), ')']);
        include_edge_branch_vec = edge_branch_vec(1:end);
        exclude_edge_branch_vec = edge_branch_vec(1:end);
        include_edge_branch_vec(branch_vehicle_edgeN) = 1;
        exclude_edge_branch_vec(branch_vehicle_edgeN) = -1;
        
        % exclude the edge
        edge_exclude_vec = edge_blacklist_vec(1:end);   % copy
        edge_exclude_vec(branch_vehicle_edgeN) = 1;
        if edge_blacklist_vec(branch_vehicle_edgeN) == 0
            branch_queue.add([edge_exclude_vec, exclude_edge_branch_vec]);
        end
        
        % force include the edge
        edge_include_vec = edge_blacklist_vec(1:end);   % copy
        % exclude all the edges (srcN, l) where l != dstN
        % find all the edges that start in srcN
        srcN_edges = false(n_vehicles*n_edges, 1);
        src_startN = (branch_vehicleN-1)*n_edges + (srcN-1)*(n_nodes-1)+1;
        src_endN = (branch_vehicleN-1)*n_edges + (srcN)*(n_nodes-1);
        srcN_edges(src_startN:src_endN) = true;
        % exclude all the edges that terminate in dstN
        srcN_edges((branch_vehicleN-1)*n_edges + nodeN2edgeN(srcN, dstN, n_nodes)) = false;
        % get the indexes of the excluded edges
        edge_include_vec(srcN_edges) = 1;
        
        % exclude all the edges (l, dstN) where l != srcN
        dstN_edges = false(n_vehicles*n_edges, 1);
        for tmp_srcN = 1:n_nodes
            if tmp_srcN == dstN || tmp_srcN == srcN
                continue;
            end
            edgeN = (branch_vehicleN-1)*n_edges + nodeN2edgeN(tmp_srcN, dstN, n_nodes);
            dstN_edges(edgeN) = true;
        end
        edge_include_vec(dstN_edges) = 1;
        
        if sum(abs(edge_include_vec - edge_blacklist_vec)) > 0
            branch_queue.add([edge_include_vec, include_edge_branch_vec]);
        end
    end

    % construct the result
    R = zeros(n_vehicles, n_edges);
    
    for vehicleN = 1:n_vehicles
        startN = best_vehicle_offset_v(vehicleN);
        endN = best_vehicle_offset_v(vehicleN+1) - 1;
        
        P_vehicle = best_P(:, startN:endN);
        
        vehicle_path_wgt_v = best_path_wgt_v(startN:endN);
        
        vehicle_pathN = vehicle_path_wgt_v > 1 - 1e-4;
        
        % check if we got an integer solution
        found_integer = any(vehicle_pathN);
        
        if ~found_integer
            disp(['got a non-integer solution for vehicle ', num2str(vehicleN), ' need to implement the branch-and-bound scheme']);
            error('Failed to find a valid solution!');
        end
        
        vehicle_path = P_vehicle(:, vehicle_pathN);
        R(vehicleN, :) = vehicle_path';
    end
    
    R_out = R*E2E_raw;
    
    toc
end