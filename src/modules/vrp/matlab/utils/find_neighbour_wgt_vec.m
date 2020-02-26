function [neighbour_wgt_vec, P_edge] = find_neighbour_wgt_vec(startN, A, M_node_edge)
    
    n_nodes = size(A, 1);

    front = java.util.ArrayList();
    visited = false(1, n_nodes);
    
    front.add([startN, 0]);
    visited(startN) = true;
    
    neighbour_wgt_vec = zeros(1, n_nodes);
    
    P_edge = zeros(n_nodes, max(max(M_node_edge)));
    
    function [vis] = all_neighbours_visited(nodeN, A_mat, visited_vec)
        neighbour_vec = A_mat(nodeN, :) > 0;
        vis = all(visited_vec(neighbour_vec));
    end
    
    while ~front.isEmpty()
        best_wgt = inf;
        bestN = -1;
        prevN = -1;
        
        for frontN = 1:front.size()
            src_node = front.get(frontN-1);
            srcN = src_node(1);
            src_wgt = src_node(2);
            
            for dstN = 1:n_nodes
                edge_wgt = A(srcN, dstN);
                
                if visited(dstN) || edge_wgt == 0
                    continue;
                end
                
                dst_wgt = src_wgt + edge_wgt;
                if dst_wgt < best_wgt
                    best_wgt = dst_wgt;
                    bestN = dstN;
                    prevN = frontN;
                end
            end
        end
        
        if bestN < 0
            error('Unable to find the next node!');
        end
        
%        disp(['visiting node ', num2str(bestN)]);
        
        % we have now jumped into node bestN
        visited(bestN) = true;
        neighbour_wgt_vec(bestN) = best_wgt;
        
        front.add([bestN, best_wgt]);
        
        if all_neighbours_visited(bestN, A, visited)
            front.remove(front.size()-1);
%            disp(['removing ', num2str(bestN), ' from the front']);
        end
        
        % check if we need to remove the previous node from the front
        src_node = front.get(prevN-1);
        srcN = src_node(1);
        if all_neighbours_visited(srcN, A, visited)
            front.remove(prevN-1);
%            disp(['removing ', num2str(srcN), ' from the front']);
        end
           
        edgeN = M_node_edge(srcN, bestN);
        P_edge(bestN, :) = P_edge(srcN, :);
        P_edge(bestN, edgeN) = 1;
        
        % check if we need to remove any other node from the front       
        for frontN = front.size():-1:1
            src_node = front.get(frontN-1);
            nodeN = src_node(1);
            if all_neighbours_visited(nodeN, A, visited)
                front.remove(frontN-1);
%                disp(['removing ', num2str(bestN), ' from the front']);
            end
        end
        
%        disp(['front size: ', num2str(front.size())]);
    end
end

