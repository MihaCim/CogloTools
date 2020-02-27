function [path_wgt_v, cost, P, vehicle_offset_v] = vrptw_solve_bnb(E, C, T, start_v, end_v, distr_vec, capacity_vec, t_start_vec, t_end_vec, eps, vehicle_edge_blacklist_vec)
    
    n_nodes = size(E, 1);
    n_edges = size(E, 2);
    n_vehicles = size(C, 1);
    
    ones_m = ones(1, n_edges);
    
    %E_whitelist = E(:, 1 - edge_blacklist_vec);
    E_src = max(-E, 0);
    
    % select the initial set of columns P
    % we can find paths by setting all weights to negative
    % and finding a path with the negative path algorithm
    vehicle_paths = cell(1, n_vehicles);
    vehicle_filtered_paths = cell(1, n_vehicles);
    vehicle_finished_v = false(1, n_vehicles);
    
    % we need to do so for each vehicle
    neg_edge_cost_v = -ones(1, n_edges);
    for vehicleN = 1:n_vehicles
        startN = start_v(vehicleN);
        endN = end_v(vehicleN);
        
        vehicle_capacity = capacity_vec(vehicleN);
        edge_time_vec = T(vehicleN, :);
        
        blacklist_startN = (vehicleN-1)*n_edges + 1;
        blacklist_endN = vehicleN*n_edges;
        edge_blacklist_vec = vehicle_edge_blacklist_vec(blacklist_startN:blacklist_endN);
        
        paths_vehicle = vrptw_neg_path( ...
            E,  ...
            neg_edge_cost_v,    ...
            edge_time_vec,   ...
            startN, ...
            endN,   ...
            distr_vec,  ...
            vehicle_capacity,   ...
            t_start_vec,    ...
            t_end_vec,   ...
            eps,     ...
            edge_blacklist_vec,     ...
            1   ...
        );
    
        n_paths = size(paths_vehicle, 1);
        if n_paths == 0
            % we did not manage to find a path from start
            % to finish for this vehicle
            error(['failed to find a path for vehicle', num2str(vehicleN)]);
        end
        
        %vehicle_paths{vehicleN} = [zeros(n_edges, 1), paths_vehicle];
        vehicle_paths{vehicleN} = paths_vehicle;
    end
    
    iterN = 1;
    while ~all(vehicle_finished_v)
        disp(['iteration: ', num2str(iterN)]);
        iterN = iterN + 1;

        % construct the path matrix and vehicle offset vector
        total_paths = 0;
        for vehicleN = 1:n_vehicles
            P_vehicle = vehicle_paths{vehicleN};
            
            blacklist_startN = (vehicleN-1)*n_edges + 1;
            blacklist_endN = vehicleN*n_edges;
            edge_blacklist_vec = vehicle_edge_blacklist_vec(blacklist_startN:blacklist_endN);
            
            path_whitelist = edge_blacklist_vec'*P_vehicle == 0;
            P_filtered = P_vehicle(:, path_whitelist);
            
            vehicle_filtered_paths{vehicleN} = P_filtered;
            total_paths = total_paths + size(P_filtered, 2);
        end
        
        % filter the paths
        P = zeros(n_edges, total_paths);
        vehicle_offset_v = zeros(1, n_vehicles+1);
        vehicle_offset_v(1) = 1;
        for vehicleN = 1:n_vehicles
            P_filtered = vehicle_filtered_paths{vehicleN};
            
            vehicle_path_num = size(P_filtered, 2);
            
            vehicle_offset_v(vehicleN+1) = vehicle_offset_v(vehicleN) + vehicle_path_num;
            
            startN = vehicle_offset_v(vehicleN);
            endN = startN + vehicle_path_num - 1;
            
            P(:, startN:endN) = P_filtered;
        end
        
        % run the dual problem on the filtered paths
        beta = vrptw_dual(   ...
            P,  ...
            vehicle_offset_v,   ...
            E,  ...
            C   ...
        );
        
        for vehicleN = 1:n_vehicles
            if vehicle_finished_v(vehicleN)
                continue;
            end
            
            blacklist_startN = (vehicleN-1)*n_edges + 1;
            blacklist_endN = vehicleN*n_edges;
            edge_blacklist_vec = vehicle_edge_blacklist_vec(blacklist_startN:blacklist_endN);
            
            c_red = C(vehicleN, :);
            edge_time_vec = T(vehicleN, :);

            for nodeN = 1:n_nodes
                % find out which edges the current node is the 
                % source of
                src_edge_v = E_src(nodeN, :);
                c_red = c_red - src_edge_v*beta(nodeN);
            end
            
%            disp(['iterN: ', num2str(iterN), ', vehicleN: ', num2str(vehicleN)]);
            
            %c_red
            
            if all(c_red >= 0)
%                disp(['vehicle ', num2str(vehicleN), ' has finished']);
                vehicle_finished_v(vehicleN) = true;
                continue;
            end
            
            rel_eps = max(abs(c_red))*eps;
            
            %disp('=======================================');
            %disp('=======================================');
            
            [P_vehicle_new, c] = vrptw_neg_path(    ...
                E,  ...
                c_red,  ...
                edge_time_vec,  ...
                start_v(vehicleN),  ...
                end_v(vehicleN),    ...
                distr_vec,  ...
                capacity_vec(vehicleN), ...
                t_start_vec,    ...
                t_end_vec,   ...
                rel_eps,     ...
                edge_blacklist_vec,     ...
                10  ...
            );
        
%            disp(['reduced cost for vehicle ', num2str(vehicleN), ': [', num2str(c(:).'), ']']);
        
            % fix for numerical errors
%             c(c > -1e-10) = 0;
%             c = min(c, 0);

            % extend the paths for this vehicle
            P_curr = vehicle_paths{vehicleN};

            n_old_paths = size(P_curr, 2);
            n_cand_paths = size(P_vehicle_new, 2);

            C_intersect = P_vehicle_new' * P_curr;

            C_old = ones(n_cand_paths, 1) * (ones_m*P_curr);
            C_new = (ones_m*P_vehicle_new)' * ones(1, n_old_paths);
            
            N_dupl = C_new == C_intersect & C_new == C_old;
            dupl_vec = N_dupl*ones(n_old_paths, 1);
            new_vec = dupl_vec == 0;

            P_new_undupl = P_vehicle_new(:, new_vec);
            c_undupl = c(new_vec);
            
            P_vehicle_extended = [vehicle_paths{vehicleN}, P_new_undupl];
            vehicle_paths{vehicleN} = P_vehicle_extended;
            
%            disp(['vehicleN: ', num2str(vehicleN), ': npaths: ', num2str(size(P_vehicle_extended, 2)), ', costs: [', num2str(c_undupl(:).'), '], n duplicates: ', num2str(length(c) - length(c_undupl)), ', rel eps: ', num2str(rel_eps)]);
            
            % if all the entries of c are zero, then
            % this vehicle is finished
            if ~any(c)
                % all the entries of c are zero
%                disp(['vehicle ', num2str(vehicleN), ' has finished']);
                vehicle_finished_v(vehicleN) = true;
            end
            if sum(new_vec) == 0
%                disp(['vehicle ', num2str(vehicleN), ' did not find any new paths']);
                vehicle_finished_v(vehicleN) = true;
            end
        end
    end
    
    % We now have the set of paths that produce the optimal
    % solution. Now we need to run the primal problem to
    % get the actual solution

    % construct the path matrix and vehicle offset vector
    total_paths = 0;
    for vehicleN = 1:n_vehicles
        P_vehicle = vehicle_paths{vehicleN};
        total_paths = total_paths + size(P_vehicle, 2);
    end

    P = zeros(n_edges, total_paths);
    vehicle_offset_v = zeros(1, n_vehicles+1);
    vehicle_offset_v(1) = 1;
    for vehicleN = 1:n_vehicles
        P_vehicle = vehicle_paths{vehicleN};

        vehicle_path_num = size(P_vehicle, 2);

        startN = vehicle_offset_v(vehicleN);
        endN = startN + vehicle_path_num - 1;
        
        vehicle_offset_v(vehicleN+1) = vehicle_offset_v(vehicleN) + vehicle_path_num;

        P(:, startN:endN) = P_vehicle;
    end
    
    [path_wgt_v, cost] = vrptw_primal(   ...
        P,  ...
        vehicle_offset_v,   ...
        E,  ...
        C   ...
    );
end