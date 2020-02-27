%% test 1 - basic graph, 2 vehicles with different costs
%           The starting node for both vehicles is 1.
%   4
%  / \
% 5 - 3
% |   |
% 1 - 2
%
E = [
    [-1, -1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0]
    [ 1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  1, -1, -1, -1,  1,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  0,  1],
    [ 0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1, -1]
];

X = [
    [ 1,  1,  1,  0,  0,  1,  0,  0,  1,  1,  1,  0],
    [ 0,  1,  1,  0,  1,  0,  0,  1,  0,  0,  0,  1]
]';

C_edge = [
    [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1],
    [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1]
];

% perturbate C so that no vehicles have the same costs
%C_edge = C_edge + 1e-5*rand(size(C_edge));

edge_time_vec = [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];

start_vec = [1, 1];
end_vec = [1, 1];

distrib_vec = [0, 4, 3, 4, 3];
capacity_vec = [10, 10];

t_start_vec = [0, 0, 0, 0, 0];
t_end_vec = [10, 10, 10, 10, 10];

R = vrptw_solve( ...
    E, ...
    C_edge, ...
    edge_time_vec, ...
    start_vec, ...
    end_vec, ...
    distrib_vec, ...
    capacity_vec, ...
    t_start_vec, ...
    t_end_vec ...
);
R

%% SMALL SCENARIO TO TEST BnB
%           The starting node for both vehicles is 1.
%   
%  
% 4 - 3
% |   |
% 1 - 2
%
% incidence matrix
E = [
    [-1,-1, 1, 0, 0, 0, 1, 0],
    [ 1, 0,-1,-1, 1, 0, 0, 0],
    [ 0, 0, 0, 1,-1,-1, 0, 1],
    [ 0, 1, 0, 0, 0, 1,-1,-1]
];

n_nodes = size(E, 1);
n_edges = size(E, 2);

% edge times and distances
% dist_vec = [ 30, 15, 30, 10, 10, 10,  2,  2,  2,  2,  2,  2,  2,  2, 10, 10, 10, 30, 15, 30];
time_vec = [  1,  1,  1,  1,  1,  1,  1,  1];

C = ones(2, n_edges);

% start and end positions
start_vec = [1, 1];
end_vec = [1, 1];

% edge distribution vector
distr_vec = [10, 10, 10, 10];

% vehicle capacities
capacity_vec = [20, 20];

% start and end times
t_start_vec = [0, 0, 0, 0];
t_end_vec =   [5, 5, 5, 5];

[R, cost] = vrptw_solve( ...
    E, ...
    C, ...
    time_vec, ...
    start_vec, ...
    end_vec, ...
    distr_vec, ...
    capacity_vec, ...
    t_start_vec, ...
    t_end_vec ...
);
R
cost

assert(abs(cost - 6) < 1e-7);

%% DELIVERABLE SCENARIO
gamma = 0;  % controls whther time or distance will be taken into account
driver_hourly_cost = 15;    % 15 EUR / h
fuel_cost = 1.5;            % 1.5 EUR / l

fuel_consump_vec = [ % [l / 100km]
    18,
    15,
    12
];
driver_cost_vec = [ % [EUR / h]
    20,
    35,
    50
];

n_vehicles = length(driver_cost_vec);

% incidence matrix
E = [
    [-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [ 1, 0,-1,-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 0,-1,-1,-1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 1, 0,-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1, 0, 1, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,-1,-1,-1, 0, 1, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1,-1, 0, 1],
    [ 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1]
];

n_nodes = size(E, 1);
n_edges = size(E, 2);

% edge times and distances
dist_vec = [ 30, 30, 30, 10, 10, 10,  2,  2,  2,  2,  2,  2,  2,  2, 10, 10, 10, 30, 30, 30];
vel_vec =  [130,130,130, 80, 80, 80, 30, 30, 30, 30, 30, 30, 30, 30, 80, 80, 80,130,130,130];
time_vec = dist_vec ./ vel_vec;

% cost
C_dist = 0.01 * fuel_cost * fuel_consump_vec * dist_vec;
C_time = driver_cost_vec * time_vec;

C = gamma*C_dist + (1 - gamma)*C_time
% perturbate C so to mitigate the absence of branch and bound
%C = C + 1e-4*rand(size(C));

% start and end positions
start_vec = [1, 2, 4];
end_vec = [1, 2, 4];

% edge distribution vector
distr_vec = [10, 10, 10, 10, 10, 10, 10, 10];

% vehicle capacities
capacity_vec = [30, 100, 30];
vehicle_colors = {'r', 'g', 'm'};

% start and end times
t_start_vec = zeros(n_edges, 1);
t_end_vec = sum(time_vec) * ones(n_edges, 1);

[R, cost] = vrptw_solve( ...
    E, ...
    C, ...
    time_vec, ...
    start_vec, ...
    end_vec, ...
    distr_vec, ...
    capacity_vec, ...
    t_start_vec, ...
    t_end_vec ...
);
R
cost

assert(cost < 36.5);

% draw the solution
coords = [
    [0, 0],
    [1, 0],
    [2, 0],
    [3, 0],
    [3, 1],
    [2, 1],
    [1, 1],
    [0, 1],
];

E_src = max(-E, 0);
E_dst = max(E, 0);
% adjacency matrix
A = E_src * E_dst';

x_min = min(coords(:, 1));
x_max = max(coords(:, 1));
y_min = min(coords(:, 2));
y_max = max(coords(:, 2));

x_range = x_max - x_min;
y_range = (y_max - y_min) * 1.25;

x_start = -0.125*x_range;
x_end = 1.125*x_range;
y_start = -0.125*y_range;
y_end = 1.125*y_range;

close;

for srcN = 1:n_nodes
    src_coords = coords(srcN, :);
    
    for dstN = 1:n_nodes
        if A(srcN, dstN) > 0
            dst_coords = coords(dstN, :);
            
            edges_src = E_src(srcN, :);
            edges_dst = E_dst(dstN, :);
            edge_ind_vec = edges_src*diag(edges_dst);
            
            dist = dist_vec*edge_ind_vec';
            time = time_vec*edge_ind_vec';
            txt = strcat('(', num2str(dist, 2), ', ', num2str(time, 2), ')');
            
            x0 = src_coords(1);
            y0 = src_coords(2);
            x1 = dst_coords(1);
            y1 = dst_coords(2);
            
            centerX = 0.5*(x0 + x1);
            centerY = 0.5*(y0 + y1);
            
            y_offset_abs = 0.03;
            x_offset_abs = -0.08;
            
            y_offset = (y1 == y0)*((y1 > 0.5)*y_offset_abs - (y1 < 0.5)*y_offset_abs*1.3);
            x_offset = (y_offset == 0)*x_offset_abs;
            
            rotation = 0;
            
            if y_offset == 0
                rotation = 90;
            end
            
            line([x0, x1], [y0, y1]);
            t = text( ...
                centerX + x_offset, centerY + y_offset, ...
                txt, ...
                'VerticalAlignment', 'middle', ...
                'HorizontalAlignment', 'center' ...
            );
            set(t, 'Rotation', rotation);
        end
    end
end

for nodeN = 1:n_nodes  
    src_coords = coords(nodeN, :);
    d_i = distr_vec(nodeN);
    
    x_txt = src_coords(1);
    y_txt = src_coords(2);
    
    offset_dir = (y_txt > 0.5)*[0, 1] + 1.6*(y_txt <= 0.5)*[0, -1];
    
    txt_offset = offset_dir*0.03;
    
    text( ...
        x_txt + txt_offset(1), y_txt + txt_offset(2), ...
        strcat(num2str(nodeN), ' (', num2str(d_i), ')'), ...
        'VerticalAlignment', 'middle', ...
        'HorizontalAlignment', 'center' ...
    );
end

axis([x_start, x_end, y_start, y_end]);

% draw the paths
for vehicleN = 1:n_vehicles
    vehicle_path = R(vehicleN, :);
    A_vehicle = E_src * diag(vehicle_path)*E_dst';
    
    color = vehicle_colors{vehicleN};
    
    for srcN = 1:n_nodes
        for dstN = 1:n_nodes
            if A_vehicle(srcN, dstN) > 0
                src_coords = coords(srcN, :);
                dst_coords = coords(dstN, :);

                x0 = src_coords(1);
                y0 = src_coords(2);
                x1 = dst_coords(1);
                y1 = dst_coords(2);
                
                centerX = 0.5*(x0 + x1);
                centerY = 0.5*(y0 + y1);

                line( ...
                    [x0, x1], ...
                    [y0, y1], ...
                    'Color', color, ...
                    'Marker', '*', ...
                    'LineWidth', 2, ...
                    'LineStyle', '--' ...
                );
            end
        end
    end
end
%% DELIVERABLE TIME SCENARIO - SLOW
gamma = 1;  % controls whther time or distance will be taken into account
driver_hourly_cost = 15;    % 15 EUR / h
fuel_cost = 1.5;            % 1.5 EUR / l

fuel_consump_vec = [ % [l / 100km]
    18,
    15,
    12
];
driver_cost_vec = [ % [EUR / h]
    20,
    35,
    50
];

n_vehicles = length(driver_cost_vec);

% incidence matrix
E = [
    [-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [ 1, 0,-1,-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 0,-1,-1,-1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 1, 0,-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1, 0, 1, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,-1,-1,-1, 0, 1, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1,-1, 0, 1],
    [ 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1]
];

n_nodes = size(E, 1);
n_edges = size(E, 2);

% edge times and distances
% dist_vec = [ 30, 15, 30, 10, 10, 10,  2,  2,  2,  2,  2,  2,  2,  2, 10, 10, 10, 30, 15, 30];
vel_vec =  [130,130,130, 80, 80, 80, 30, 30, 30, 30, 30, 30, 30, 30, 80, 80, 80,130,130,130];
time_vec = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
dist_vec = time_vec .* vel_vec;
% time_vec = dist_vec ./ vel_vec;

% cost
C_dist = 0.01 * fuel_cost * fuel_consump_vec * dist_vec;
C_time = driver_cost_vec * time_vec;

C = gamma*C_dist + (1 - gamma)*C_time;

% start and end positions
start_vec = [1, 1, 1];
end_vec = [1, 1, 1];

% edge distribution vector
distr_vec = [10, 10, 10, 10, 10, 10, 10, 10];

% vehicle capacities
capacity_vec = [60, 60, 60];

% start and end times
t_start_vec = [0, 2, 4, 6, 6, 4, 2, 0];
t_end_vec =   [2, 4, 6, 8, 8, 6, 4, 2];

[R, cost] = vrptw_solve( ...
    E, ...
    C, ...
    time_vec, ...
    start_vec, ...
    end_vec, ...
    distr_vec, ...
    capacity_vec, ...
    t_start_vec, ...
    t_end_vec ...
);
R
cost

assert(cost <= 286.65);

% draw the solution
vehicle_colors = {'r', 'g', 'm'};
coords = [
    [0, 0],
    [1, 0],
    [2, 0],
    [3, 0],
    [3, 1],
    [2, 1],
    [1, 1],
    [0, 1],
];

E_src = max(-E, 0);
E_dst = max(E, 0);
% adjacency matrix
A = E_src * E_dst';

x_min = min(coords(:, 1));
x_max = max(coords(:, 1));
y_min = min(coords(:, 2));
y_max = max(coords(:, 2));

x_range = x_max - x_min;
y_range = (y_max - y_min) * 1.25;

x_start = -0.125*x_range;
x_end = 1.125*x_range;
y_start = -0.125*y_range;
y_end = 1.125*y_range;

close;

for srcN = 1:n_nodes
    src_coords = coords(srcN, :);
    
    for dstN = 1:n_nodes
        if A(srcN, dstN) > 0
            dst_coords = coords(dstN, :);
            
            edges_src = E_src(srcN, :);
            edges_dst = E_dst(dstN, :);
            edge_ind_vec = edges_src*diag(edges_dst);
            
            dist = dist_vec*edge_ind_vec';
            time = time_vec*edge_ind_vec';
            txt = strcat('(', num2str(dist, 2), ', ', num2str(time, 2), ')');
            
            x0 = src_coords(1);
            y0 = src_coords(2);
            x1 = dst_coords(1);
            y1 = dst_coords(2);
            
            centerX = 0.5*(x0 + x1);
            centerY = 0.5*(y0 + y1);
            
            y_offset_abs = 0.03;
            x_offset_abs = -0.08;
            
            y_offset = (y1 == y0)*((y1 > 0.5)*y_offset_abs - (y1 < 0.5)*y_offset_abs*1.3);
            x_offset = (y_offset == 0)*x_offset_abs;
            
            rotation = 0;
            
            if y_offset == 0
                rotation = 90;
            end
            
            line([x0, x1], [y0, y1]);
            t = text( ...
                centerX + x_offset, centerY + y_offset, ...
                txt, ...
                'VerticalAlignment', 'middle', ...
                'HorizontalAlignment', 'center' ...
            );
            set(t, 'Rotation', rotation);
        end
    end
end

for nodeN = 1:n_nodes  
    src_coords = coords(nodeN, :);
    d_i = distr_vec(nodeN);
    
    x_txt = src_coords(1);
    y_txt = src_coords(2);
    
    offset_dir = (y_txt > 0.5)*[0, 1] + 1.6*(y_txt <= 0.5)*[0, -1];
    
    txt_offset = offset_dir*0.03;
    
    text( ...
        x_txt + txt_offset(1), y_txt + txt_offset(2), ...
        strcat(num2str(nodeN), ' (', num2str(d_i), ')'), ...
        'VerticalAlignment', 'middle', ...
        'HorizontalAlignment', 'center' ...
    );
end

axis([x_start, x_end, y_start, y_end]);

% draw the paths
for vehicleN = 1:n_vehicles
    vehicle_path = R(vehicleN, :);
    A_vehicle = E_src * diag(vehicle_path)*E_dst';
    
    color = vehicle_colors{vehicleN};
    
    for srcN = 1:n_nodes
        for dstN = 1:n_nodes
            if A_vehicle(srcN, dstN) > 0
                src_coords = coords(srcN, :);
                dst_coords = coords(dstN, :);

                x0 = src_coords(1);
                y0 = src_coords(2);
                x1 = dst_coords(1);
                y1 = dst_coords(2);
                
                centerX = 0.5*(x0 + x1);
                centerY = 0.5*(y0 + y1);

                line( ...
                    [x0, x1], ...
                    [y0, y1], ...
                    'Color', color, ...
                    'Marker', '*', ...
                    'LineWidth', 2, ...
                    'LineStyle', '--' ...
                );
            end
        end
    end
end

%% DELIVERABLE TIME SCENARIO - 2 cars
gamma = 1;  % controls whther time or distance will be taken into account
driver_hourly_cost = 15;    % 15 EUR / h
fuel_cost = 1.5;            % 1.5 EUR / l

fuel_consump_vec = [ % [l / 100km]
    18,
    15
];
driver_cost_vec = [ % [EUR / h]
    20,
    35
];

n_vehicles = length(driver_cost_vec);

% incidence matrix
E = [
    [-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [ 1, 0,-1,-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 0,-1,-1,-1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 1, 0,-1,-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1, 0, 1, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,-1,-1,-1, 0, 1, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1,-1, 0, 1],
    [ 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,-1,-1]
];

n_nodes = size(E, 1);
n_edges = size(E, 2);

% edge times and distances
% dist_vec = [ 30, 15, 30, 10, 10, 10,  2,  2,  2,  2,  2,  2,  2,  2, 10, 10, 10, 30, 15, 30];
vel_vec =  [130,130,130, 80, 80, 80, 30, 30, 30, 30, 30, 30, 30, 30, 80, 80, 80,130,130,130];
time_vec = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
dist_vec = time_vec .* vel_vec;
% time_vec = dist_vec ./ vel_vec;

% cost
C_dist = 0.01 * fuel_cost * fuel_consump_vec * dist_vec;
C_time = driver_cost_vec * time_vec;

%rng(1);
C = gamma*C_dist + (1 - gamma)*C_time;
%C = C + 1e-5*rand(size(C));

% start and end positions
start_vec = [1, 1];
end_vec = [1, 1];

% edge distribution vector
distr_vec = [0, 10, 10, 10, 10, 10, 10, 10];

% vehicle capacities
capacity_vec = [60, 60];

% start and end times
t_start_vec = [0, 2, 4, 6, 6, 4, 2, 0];
t_end_vec =   [30, 4, 6, 8, 8, 6, 4, 2];

[R, cost] = vrptw_solve( ...
    E, ...
    C, ...
    time_vec, ...
    start_vec, ...
    end_vec, ...
    distr_vec, ...
    capacity_vec, ...
    t_start_vec, ...
    t_end_vec ...
);
R
cost

assert(cost <= 261.45);

% draw the solution
vehicle_colors = {'r', 'g', 'm'};
coords = [
    [0, 0],
    [1, 0],
    [2, 0],
    [3, 0],
    [3, 1],
    [2, 1],
    [1, 1],
    [0, 1],
];

E_src = max(-E, 0);
E_dst = max(E, 0);
% adjacency matrix
A = E_src * E_dst';

x_min = min(coords(:, 1));
x_max = max(coords(:, 1));
y_min = min(coords(:, 2));
y_max = max(coords(:, 2));

x_range = x_max - x_min;
y_range = (y_max - y_min) * 1.25;

x_start = -0.125*x_range;
x_end = 1.125*x_range;
y_start = -0.125*y_range;
y_end = 1.125*y_range;

close;

for srcN = 1:n_nodes
    src_coords = coords(srcN, :);
    
    for dstN = 1:n_nodes
        if A(srcN, dstN) > 0
            dst_coords = coords(dstN, :);
            
            edges_src = E_src(srcN, :);
            edges_dst = E_dst(dstN, :);
            edge_ind_vec = edges_src*diag(edges_dst);
            
            dist = dist_vec*edge_ind_vec';
            time = time_vec*edge_ind_vec';
            txt = strcat('(', num2str(dist, 2), ', ', num2str(time, 2), ')');
            
            x0 = src_coords(1);
            y0 = src_coords(2);
            x1 = dst_coords(1);
            y1 = dst_coords(2);
            
            centerX = 0.5*(x0 + x1);
            centerY = 0.5*(y0 + y1);
            
            y_offset_abs = 0.03;
            x_offset_abs = -0.08;
            
            y_offset = (y1 == y0)*((y1 > 0.5)*y_offset_abs - (y1 < 0.5)*y_offset_abs*1.3);
            x_offset = (y_offset == 0)*x_offset_abs;
            
            rotation = 0;
            
            if y_offset == 0
                rotation = 90;
            end
            
            line([x0, x1], [y0, y1]);
            t = text( ...
                centerX + x_offset, centerY + y_offset, ...
                txt, ...
                'VerticalAlignment', 'middle', ...
                'HorizontalAlignment', 'center' ...
            );
            set(t, 'Rotation', rotation);
        end
    end
end

for nodeN = 1:n_nodes  
    src_coords = coords(nodeN, :);
    d_i = distr_vec(nodeN);
    
    x_txt = src_coords(1);
    y_txt = src_coords(2);
    
    offset_dir = (y_txt > 0.5)*[0, 1] + 1.6*(y_txt <= 0.5)*[0, -1];
    
    txt_offset = offset_dir*0.03;
    
    text( ...
        x_txt + txt_offset(1), y_txt + txt_offset(2), ...
        strcat(num2str(nodeN), ' (', num2str(d_i), ')'), ...
        'VerticalAlignment', 'middle', ...
        'HorizontalAlignment', 'center' ...
    );
end

axis([x_start, x_end, y_start, y_end]);

% draw the paths
for vehicleN = 1:n_vehicles
    vehicle_path = R(vehicleN, :);
    A_vehicle = E_src * diag(vehicle_path)*E_dst';
    
    color = vehicle_colors{vehicleN};
    
    for srcN = 1:n_nodes
        for dstN = 1:n_nodes
            if A_vehicle(srcN, dstN) > 0
                src_coords = coords(srcN, :);
                dst_coords = coords(dstN, :);

                x0 = src_coords(1);
                y0 = src_coords(2);
                x1 = dst_coords(1);
                y1 = dst_coords(2);
                
                centerX = 0.5*(x0 + x1);
                centerY = 0.5*(y0 + y1);

                line( ...
                    [x0, x1], ...
                    [y0, y1], ...
                    'Color', color, ...
                    'Marker', '*', ...
                    'LineWidth', 2, ...
                    'LineStyle', '--' ...
                );
            end
        end
    end
end

%% SIMPLE TIME TEST
gamma = 1;  % controls whther time or distance will be taken into account
driver_hourly_cost = 15;    % 15 EUR / h
fuel_cost = 1.5;            % 1.5 EUR / l

fuel_consump_vec = [ % [l / 100km]
    18,
    15
];
driver_cost_vec = [ % [EUR / h]
    20,
    35
];

n_vehicles = length(driver_cost_vec);

% incidence matrix
E = [
    [-1,-1, 1, 0, 0, 0, 1, 0],
    [ 1, 0,-1,-1, 1, 0, 0, 0],
    [ 0, 0, 0, 1,-1,-1, 0, 1],
    [ 0, 1, 0, 0, 0, 1,-1,-1]
];

n_nodes = size(E, 1);
n_edges = size(E, 2);

% edge times and distances
% dist_vec = [ 30, 15, 30, 10, 10, 10,  2,  2,  2,  2,  2,  2,  2,  2, 10, 10, 10, 30, 15, 30];
vel_vec =  [130,130,130, 80, 80, 80, 30, 30];
time_vec = [  1,  1,  1,  1,  1,  1,  1,  1];
dist_vec = [  1,  1,  1,  1,  1,  1,  1,  1];
% time_vec = dist_vec ./ vel_vec;

% cost
C_dist = 0.01 * fuel_cost * fuel_consump_vec * dist_vec;
C_time = driver_cost_vec * time_vec;

C = [
    [1, 1, 1, 2, 2, 1, 1, 1],
    [1, 1, 1, 2, 2, 1, 1, 1]
];

% start and end positions
start_vec = [1, 1];
end_vec = [1, 1];

% edge distribution vector
distr_vec = [10, 10, 10, 10];

% vehicle capacities
capacity_vec = [60, 60];

% start and end times
t_start_vec = [0, 1, 2, 1];
t_end_vec =   [8, 2, 3, 2];

[R, cost] = vrptw_solve( ...
    E, ...
    C, ...
    time_vec, ...
    start_vec, ...
    end_vec, ...
    distr_vec, ...
    capacity_vec, ...
    t_start_vec, ...
    t_end_vec ...
);
R
cost
assert(cost == 6);

%% Test on a random graph
n_loc = 10;
p_start = [0, 0];
center_left = [-100, 100];
center_right = [100, 100];
std_dev = 30;

speed = 90; % km / h
fuel_consumpt = 10; % l / 100km
fuel_cost = 1.3;    % EUR / l
driver_cost = 30;   % EUR / h

sigma = std_dev*std_dev;

% set a random seed
rng(1);

dist = @(x, y) sqrt((x(1) - y(1))^2 + (x(2) - y(2))^2);

P = zeros(n_loc, 2);

P(1, :) = p_start;

n_loc_left = ceil(0.5*(n_loc-1));
n_loc_right = floor(0.5*(n_loc-1));

P_left = mvnrnd(center_left, [sigma, 0; 0, sigma], n_loc_left);
P_right = mvnrnd(center_right, [sigma, 0; 0, sigma], n_loc_right);

P(2:(1+n_loc_left), :) = P_left;
P((2+n_loc_left):end, :) = P_right;

% triangulate the points
simplices = delaunay(P);
n_simplices = size(simplices, 1);

A = inf(n_loc, n_loc);

for simplexN = 1:n_simplices
    simplex = simplices(simplexN, :);
    
    n0 = min(simplex);
    n2 = max(simplex);
    n1 = max(min(simplex(1), simplex(2)), min(max(simplex(1), simplex(2)), simplex(3)));
    
    disp(['simplex: [', num2str(n0), ', ', num2str(n1), ', ', num2str(n2), ']']);
    
    p0 = P(n0, :);
    p1 = P(n1, :);
    p2 = P(n2, :);
    
    d_01 = dist(p0, p1);
    d_02 = dist(p0, p2);
    d_12 = dist(p1, p2);
    
    A(n0, n1) = d_01;
    A(n1, n0) = d_01;
    A(n0, n2) = d_02;
    A(n2, n0) = d_02;
    A(n1, n2) = d_12;
    A(n2, n1) = d_12;
end

n_edges = length(find(A < inf));
n_vehicles = 4;
vehicle_colors = { 'red', 'blue', 'green', 'magenta' };

E = zeros(n_loc, n_edges);
C = zeros(n_vehicles, n_edges);

t_vec = zeros(1, n_edges);

distr_vec = ones(1, n_loc);
distr_vec(1) = 0;

start_v = ones(1, n_vehicles);
end_v = ones(1, n_vehicles);

capacity_vec = 0.5*n_loc*ones(1, n_vehicles);

% construct the incidence matrix
edgeN = 1;
for srcN = 1:n_loc
    for dstN = 1:n_loc
        if A(srcN, dstN) >= inf
            continue;
        end
        
        E(srcN, edgeN) = -1;
        E(dstN, edgeN) = 1;
        
        d_ij = A(srcN, dstN);   % km
        t_ij = d_ij / speed;
        
        c_f = d_ij*0.01*fuel_consumpt*fuel_cost;
        c_d = t_ij*driver_cost;
        
        c_ij = c_f + c_d;
        
        for vehicleN = 1:n_vehicles
            C(vehicleN, edgeN) = c_ij;
        end
        
        t_vec(edgeN) = t_ij;
        
        edgeN = edgeN + 1;
    end
end

t_start_vec = zeros(1, n_edges);
t_end_vec = sum(t_vec)*ones(1, n_edges);

[vehicle_edges, cost] = vrptw_solve(E, C, t_vec, start_v, end_v, distr_vec, capacity_vec, t_start_vec, t_end_vec);

% plot the results
n_roads = 0.5*n_edges;
R = zeros(n_roads, 4);

node_to_road_map = zeros(n_loc, n_loc);
edge_to_road_map = zeros(1, n_edges);

roadN = 1;
for srcN = 1:n_loc
    for dstN = 1:(srcN-1)
        if A(srcN, dstN) >= inf
            continue;
        end
        
        p0 = P(srcN, :);
        p1 = P(dstN, :);
        R(roadN, 1:2) = p0;
        R(roadN, 3:4) = p1;
        
        node_to_road_map(srcN, dstN) = roadN;
        node_to_road_map(dstN, srcN) = roadN;
        
        roadN = roadN + 1;
    end
end

edgeN = 1;
for srcN = 1:n_loc
    for dstN = 1:n_loc
        if A(srcN, dstN) >= inf
            continue;
        end
        roadN = node_to_road_map(srcN, dstN);
        edge_to_road_map(edgeN) = roadN;
        edgeN = edgeN + 1;
    end
end

% plot
line_opacity = 0.2;

scatter(p_start(1), p_start(2), 'gx');
hold on;

disp('plotting roads');
for roadN = 1:n_roads
    p0 = R(roadN, 1:2);
    p1 = R(roadN, 3:4);
    
    x_vec = [p0(1), p1(1)];
    y_vec = [p0(2), p1(2)];
    
    line(x_vec, y_vec, 'color', 1 - [line_opacity, line_opacity, line_opacity]);
end

disp('plotting distribution plans');
for vehicleN = 1:n_vehicles
    edges_visited = find(vehicle_edges(vehicleN, :) > 0);
    for edge_idx = 1:length(edges_visited)
        edgeN = edges_visited(edge_idx);
        roadN = edge_to_road_map(edgeN);
        
        disp(['roadN: ', num2str(roadN)]);
        
        p0 = R(roadN, 1:2);
        p1 = R(roadN, 3:4);
    
        x_vec = [p0(1), p1(1)];
        y_vec = [p0(2), p1(2)];
    
        line(x_vec, y_vec, 'color', vehicle_colors{vehicleN});
    end
end

disp('plotting locations');
scatter(P_left(:, 1), P_left(:, 2), 'b');
scatter(P_right(:, 1), P_right(:, 2), 'r');

hold off;