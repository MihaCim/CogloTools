function [P, c] = vrptw_neg_path(E, cost_vec, time_vec, startN, endN, distr_vec, capacity, t_start, t_end, eps, edge_blacklist_vec, mn_paths)
    % A dynamic program that finds a path with negative cost that
    % satisfies the capacity constraints, the temporal constrints,
    % starts in node startN and ends in node endN.
    %
    % E - the directed graph incidence matrix
    % cost_vec - a vector of edge costs
    % time_vec - a vector of edge travel times
    % startN - index of the start node
    % endN - index of the end node
    % distr_vec - the vector of distribution amounts
    
    n_nodes = size(E, 1);
    n_edges = size(E, 2);
    
    mx_path_len = (startN == endN)*n_nodes + (startN ~= endN)*(n_nodes-1);
    
    E_plus = max(E, 0);
    E_minus = max(-E, 0);
    
    neg_sum = -sum(min(cost_vec, 0));
    disp(['searching, negative sum: ', num2str(neg_sum)]);
    
    J = 1:n_edges;
    
    hack_list = java.util.ArrayList();
    function label = create_label(cost, time, capacity, edge_vec, nodes_visited_vec)
        %label = javaArray('java.lang.Object', 5);
        %label(1) = java.lang.Double(cost);
        %label(2) = java.lang.Double(time);
        %label(3) = java.lang.Double(capacity);
        %label(4) = edge_vec;
        %label(5) = nodes_visited_vec;
        
        hack_list.add({cost, time, capacity, edge_vec, nodes_visited_vec});
        label = hack_list.get(0);
        hack_list.remove(0);
    end

    function [dom] = dominates(label1, label2)
        node_vec1 = label1(5);
        node_vec2 = label2(5);
        is_subpath = sum(node_vec1) == node_vec2'*node_vec1;
        
        dom = is_subpath && ...
                label1(1) <= label2(1) && ...
                label1(2) <= label2(2) && ...
                label1(3) <= label2(3);
    end
    
    % compute transition matrices
    function [A] = get_adj_mat(edge_vec)
        % XXX: Important! Must handle NaN values manually!
        E_minus_wgt = E_minus * sparse(J, J, 1 ./ edge_vec);
        E_minus_wgt(isnan(E_minus_wgt)) = 0;
        A = E_minus_wgt * E_plus';
        A(isnan(A)) = 0;
        A = 1 ./ A;
    end
    C_mat = get_adj_mat(cost_vec);
    T_mat = get_adj_mat(time_vec);
    
    % compute the mapping (nodeN x nodeN) -> edgeN
    M_node_edge = E_minus * sparse(J, J, J) * E_plus';
    
    % matrix of visited edges for each of the current paths
    label_v = java.util.ArrayList();
    for nodeN = 1:n_nodes
        label_v.add(java.util.ArrayList());
    end
    init_nodes_visited = zeros(1, n_nodes);
    init_nodes_visited(startN) = 1;
    label_v.get(startN-1).add(create_label( ...
        0, ...
        0, ...
        0, ...
        zeros(1, n_edges), ...
        init_nodes_visited ...
    ));

    node_neighbour_vec = java.util.ArrayList();
    for srcN = 1:n_nodes
        neighbour_vec = java.util.ArrayList();
        for dstN = 1:n_nodes
            edgeN = M_node_edge(srcN, dstN);

            if edgeN == 0 || edge_blacklist_vec(edgeN) == 1   % the edge does not exist
                continue
            end
            
            neighbour_vec.add(dstN);
        end
        node_neighbour_vec.add(neighbour_vec);
    end

    % iterate until you find a path that ends in
    % the terminal node and has negative cost
    iterN = 1;
    finished = false;
    
    n_candidates = 0;
    
    solutions = {};
    n_neg = 0;
    while ~finished && iterN <= mx_path_len
        one_found = false;
        
        if mod(iterN, 1) == 0
            disp(['path length: ', num2str(iterN), ', n candidates: ', num2str(n_candidates)]);
        end
        
        new_label_v = java.util.ArrayList();
        n_candidates = 0;
        
        for nodeN = 1:n_nodes
            new_label_v.add(java.util.ArrayList());
        end

        for prevN = 1:n_nodes
            prev_labels = label_v.get(prevN-1);
            neighbour_vec = node_neighbour_vec.get(prevN-1);
            
            for labelN = 0:prev_labels.size()-1    
                for neighN = 0:(neighbour_vec.size()-1)
                    nodeN = neighbour_vec.get(neighN);
                    edgeN = M_node_edge(prevN, nodeN);
                    
                    %disp(['checking: ', num2str(prevN), ' -> ', num2str(nodeN)]);

                    prev_label = prev_labels.get(labelN);

                    prev_cost = prev_label(1);
                    prev_time = prev_label(2);
                    prev_capacity = prev_label(3);
                    prev_edge_vec = prev_label(4);
                    prev_nodes_visited_vec = prev_label(5);
                    
                    is_node_visited = prev_nodes_visited_vec(nodeN);
                    is_terminating = nodeN == endN;

                    c_ij = C_mat(prevN, nodeN);
                    t_ij = T_mat(prevN, nodeN);
                    d_i = distr_vec(nodeN) * (1 - is_node_visited) * (1 - is_terminating);

                    new_cost = prev_cost + c_ij;
                    if is_node_visited
                        new_time = prev_time + t_ij;
                    else
                        new_time = max(t_start(nodeN), prev_time + t_ij);
                    end
                    new_capacity = prev_capacity + d_i;
                    
                    new_edge_vec = prev_edge_vec(1:end);    % copy
                    new_nodes_visited = prev_nodes_visited_vec(1:end);  % copy

                    % mark the edge visited
                    new_edge_vec(edgeN) = 1;
                    % mark the node as visited
                    new_nodes_visited(nodeN) = 1;

                    cost_valid = new_cost <= neg_sum;
                    time_valid = new_time <= t_end(nodeN) || logical(is_node_visited);
                    capacity_valid = new_capacity <= capacity;
                    node_visited = ~is_terminating && prev_nodes_visited_vec(nodeN) == 1;
                                        
                    if ~cost_valid || ~time_valid || ~capacity_valid || node_visited
                        %disp('invalid path');
                        continue
                    end

                    new_label = create_label( ...
                        new_cost, ...
                        new_time, ...
                        new_capacity, ...
                        new_edge_vec, ...
                        new_nodes_visited ...
                    );

                    % update the labels of the new node
                    % remove any labels that the current label dominates
                    % and only add the current label if it is not dominated
                    curr_labels = label_v.get(nodeN-1);
                    new_labels = new_label_v.get(nodeN-1);

                    is_dominated = false;
                    for curr_labelN = 0:curr_labels.size()-1
                        curr_node_label = curr_labels.get(curr_labelN);

                        if dominates(new_label, curr_node_label)
                            %disp('removing an exising label');
                            %removed_labels.add(curr_labelN);
                            % TODO: I think I can break here
                            break;
                            %continue;
                        end

                        if dominates(curr_node_label, new_label)
                            is_dominated = true;
                            break;
                        end
                    end

                    if ~is_dominated
                        one_found = true;
                        new_labels.add(new_label);
                        n_candidates = n_candidates + 1;
                    end
                end
            end
        end
        
        label_v = new_label_v;

        % make sure that we were able to find the
        % previous node
        if ~one_found
            % we failed to advance to the next step
            % no valid solution found
            %disp('No solution found!');
            break;
        end

        % check to see if we found a path with negative cost
        end_labels = label_v.get(endN-1);
        n_end_labels = end_labels.size();
        
        for labelN = 0:(n_end_labels-1);
            end_label = end_labels.get(labelN);
            end_cost = end_label(1);
            
            % fix numerical errors
             if abs(end_cost) < eps
                 end_cost = 0;
             end
            
            if end_cost <= 0
                % we have found a zero cost solution
                % add it to the list of solutions
                solutions{end+1} = {end_label, end_cost};
            end
            
            if end_cost < -eps
                n_neg = n_neg + 1;
                if n_neg >= mn_paths
                    finished = true;
                    break;
                end
            end
        end

        iterN = iterN + 1;
    end
    
    n_solutions = size(solutions, 2);
    
%    disp(['final num solutions: ', num2str(n_solutions)]);
    
    P = zeros(n_edges, n_solutions);
    c = zeros(n_solutions, 1);
    
    for solutionN = 1:n_solutions
        solution = solutions{solutionN};
        
        end_label = solution{1};
        end_cost = solution{2};
        
        neg_path = end_label(4);
        
        P(:, solutionN) = neg_path;
        c(solutionN) = end_cost;
    end
% 
%     if size(P, 1) > 0
%         disp(['found ', num2str(n_solutions), ' solutions']);
%     end
end