function [ A ] = incidence2adj_mat(E, wgt_vec)
    % Transforms a directed incidence matrix to an adjacency
    % matrix.
    %
    % Parameters:
    % E - a directed incidence matrix representation of the graph
    % wgt_vec - a vector of edge weights
    E_out = max(E, 0);
    E_in = max(-E, 0);

    A = E_out * diag(wgt_vec) * E_in';
end

