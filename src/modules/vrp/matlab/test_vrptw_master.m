%% test 1 - one vehicle, two paths
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
    [ 1,  2,  1, 10, 10,  1,  1,  1,  1,  2,  1,  1]
]';

y = vrptw_master(X, E, C_edge);
y

%% test 1 - 2 vehicles, 4 paths
E = [
    [-1, -1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0]
    [ 1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  1, -1, -1, -1,  1,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  0,  1],
    [ 0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1, -1]
];

X = [
    [ 1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  1,  0,  0,  0,  0,  0,  0,  1,  1,  0,  1],
    [ 0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0]
]';

C_edge = [
     [ 1,  2,  1, 10, 10,  1,  1,  1,  1,  2,  1,  1],
     [ 1,  2,  1, 10, 10,  1,  1,  1,  1,  2,  1,  1]
]';

C_edge(:, 1) = C_edge(:, 1)*1.5;

R = vrptw_master(X, E, C_edge);
R'

%% Subproblem Test 1
E = [
    [ -1, -1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0],
    [  1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  1, -1, -1, -1,  1,  0,  0,  1,  0],
    [  0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  0,  1],
    [  0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1, -1]
];
c = [ -1,  1, -1, -1, -1,  1, -1,  1,  1,  1, -1,  1];
%c = ones(1, 12);
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2];
capacity = 10;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

path = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);

expected = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0];
diff = norm(path - expected);
assert(diff < 1e-9, 'Subproblem test 1 failed!');

%% Subproblem Test 2: unreachable negative cycle in the graph
E = [
    [ -1, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [  1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  1, -1, -1, -1,  1,  0,  1,  0],
    [  0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  1],
    [  0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1]
];
c = [  2, -3,  2,  1,  1, -1, -1, -1, -1, -1, -1];
%c = ones(1, 12);
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2];
capacity = 10;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);

expected = [0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0];
expected_cost = -1;

diff = norm(path - expected);
assert(abs(cost - expected_cost) < 1e-9, 'Subproblem test 2 failed! Invalid cost!');
assert(diff < 1e-9, 'Subproblem test 2 failed! Invalid path!');

%% Subproblem Test 3: negative cycle in the graph
E = [
    [ -1,  0,  0,  0,  0,  0],
    [  1, -1,  1,  0,  0,  0],
    [  0,  1, -1, -1,  0,  0],
    [  0,  0,  0,  1, -1,  0],
    [  0,  0,  0,  0,  1, -1],
    [  0,  0,  0,  0,  0,  1]
];
c = [ -2, -1, -1,  1,  1,  0];
%c = ones(1, 12);
t = [  1,  1,  1,  1,  1,  1];
d = [0, 3, 1, 1, 2, 0];
capacity = 10;

t_start = [ 0,  0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10, 10];

startN = 1;
endN = 6;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);

expected = [1, 1, 0, 1, 1, 1];
expected_cost = -1;

diff = norm(path - expected);
assert(abs(cost - expected_cost) < 1e-9, 'Subproblem test 2 failed! Invalid cost!');
assert(diff < 1e-9, 'Subproblem test 2 failed! Invalid path!');

%% Subproblem Test 4: only positive edges
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  1,  0],
    [  0,  0,  0,  0,  1,  0, -1, -1,  0,  1],
    [  1,  0,  0,  0,  0,  1,  0,  1, -1, -1]
];
c = [ 3,  2,  1,  1,  1,  1,  1,  1,  1,  1];
%c = ones(1, 12);
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2];
capacity = 10;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);

assert(size(path, 1) == 0, 'Subproblem test 4 failed! Got more than 0 paths!');
assert(size(cost, 1) == 0, 'Subproblem test 4 failed! Got more than 0 costs!');

%% Subproblem Test 5: not enough capacity
% It should return a path that does not cover the entire
% set of nodes.
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  1,  0],
    [  0,  0,  0,  0,  1,  0, -1, -1,  0,  1],
    [  1,  0,  0,  0,  0,  1,  0,  1, -1, -1]
];
c = [ 3, -2, -1, -1,  1, -1,  1,  1, -1,  1];
%c = ones(1, 12);
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2];
capacity = 5;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);

assert(size(path, 1) == 0, 'Subproblem test 4 failed! Got more than 0 paths!');
assert(size(cost, 1) == 0, 'Subproblem test 4 failed! Got more than 0 costs!');

%% Subproblem Test 6: two negative paths of equal length
% It should return both paths
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  0,  0,  1],
    [  0,  0,  0,  0,  1,  0, -1, -1,  1,  0,  0],
    [  1,  0,  0,  0,  0,  0,  0,  1, -1, -1,  0],
    [  0,  0,  0,  0,  0,  1,  0,  0,  0,  1, -1]
];

c = [  3, -2, -1, -1, -1, -3, -1, -1, -1, -3, -2];
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2, 1];
capacity = 10;

t_start = [ 0,  0,  0,  0,  0, 0];
t_end =   [10, 10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);
expected_path1 = [1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0];
expected_cost1 = -2;
expected_path2 = [1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1];
expected_cost2 = -5;

assert(norm(expected_path1 - path(1, :)) == 0, 'Subproblem test 4 failed! One of the paths is invalid!');
assert(expected_cost1 - cost(1) == 0, 'Subproblem test 4 failed! One of the costs is invalid!');
assert(norm(expected_path2 - path(2, :)) == 0, 'Subproblem test 4 failed! One of the paths is invalid!');
assert(expected_cost2 - cost(2) == 0, 'Subproblem test 4 failed! One of the costs is invalid!');

%% Subproblem Test 7: the shortest path takes too long
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  1,  0],
    [  0,  0,  0,  0,  1,  0, -1, -1,  0,  1],
    [  1,  0,  0,  0,  0,  1,  0,  1, -1, -1]
];
c = [  3, -2, -1, -1,  1, -1, -1,  1, -1,  1];
t = [  1,  1,  3,  3,  1,  6,  1,  1,  6,  1];
d = [0, 1, 3, 2, 2];
capacity = 10;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);
expected_path1 = [1, 1, 0, 1, 0, 0, 1, 0, 0, 1];
expected_cost1 = 0;

assert(norm(expected_path1 - path(1, :)) == 0, 'Subproblem test 4 failed! One of the paths is invalid!');
assert(expected_cost1 - cost(1) == 0, 'Subproblem test 4 failed! One of the costs is invalid!');

%% Subproblem Test 8: two negative paths of equal length
% but one should not be found because of the temporal constraints
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  0,  0,  1],
    [  0,  0,  0,  0,  1,  0, -1, -1,  1,  0,  0],
    [  1,  0,  0,  0,  0,  0,  0,  1, -1, -1,  0],
    [  0,  0,  0,  0,  0,  1,  0,  0,  0,  1, -1]
];

c = [  3, -2, -1, -1, -1, -3, -1, -1, -1, -3, -2];
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2, 1];
capacity = 10;

t_start = [ 0,  8,  6,  3,  2,  8];
t_end =   [10, 10, 10,  3,  3,  9];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);
expected_path1 = [1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0];
expected_cost1 = -2;

assert(size(path, 1) == 1, 'Found too many paths');
assert(norm(expected_path1 - path(1, :)) == 0, 'Subproblem test 4 failed! One of the paths is invalid!');
assert(expected_cost1 - cost(1) == 0, 'Subproblem test 4 failed! One of the costs is invalid!');

%% Subproblem Test 9: should not find any paths because of
% temporal constraints
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  0,  0,  1],
    [  0,  0,  0,  0,  1,  0, -1, -1,  1,  0,  0],
    [  1,  0,  0,  0,  0,  0,  0,  1, -1, -1,  0],
    [  0,  0,  0,  0,  0,  1,  0,  0,  0,  1, -1]
];

c = [  3, -2, -1, -1, -1, -3, -1, -1, -1, -3, -2];
t = [  1,  1,  1,  1,  1,  1,  6,  1,  1,  1,  1];
d = [0, 1, 3, 2, 2, 1];
capacity = 10;

t_start = [ 0,  8,  6,  3,  2,  8];
t_end =   [10, 10, 10,  3,  3,  9];

startN = 1;
endN = 1;

[path, ~] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);
%expected_path1 = [1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0];

assert(size(path, 1) == 0, 'Found too many paths');

%% Subproblem Test 10: dropoff at a the end (and start) point
E = [
    [ -1,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  1,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1,  1,  0,  1,  0],
    [  0,  0,  0,  0,  1,  0, -1, -1,  0,  1],
    [  1,  0,  0,  0,  0,  1,  0,  1, -1, -1]
];
c = [  3, -2, -1, -1,  1, -1, -1,  1, -1,  1];
t = [  1,  1,  3,  3,  1,  6,  1,  1,  6,  1];
d = [1, 1, 3, 2, 2];
capacity = 9;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);
expected_path1 = [1, 1, 0, 1, 0, 0, 1, 0, 0, 1];
expected_cost1 = 0;

assert(norm(expected_path1 - path(1, :)) == 0, 'Subproblem test 4 failed! One of the paths is invalid!');
assert(expected_cost1 - cost(1) == 0, 'Subproblem test 4 failed! One of the costs is invalid!');

%% Subproblem Test 11: there is only one non-positive path which costs 0
E = [
    [ -1,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0],
    [  0, -1, -1,  0,  1,  0,  0,  0,  0,  0,  0],
    [  0,  0,  1, -1, -1, -1, -1,  1,  0,  1,  0],
    [  0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  1],
    [  1,  0,  0,  0,  0,  0,  1,  0,  1, -1, -1]
];
c = [  3,  2, -1, -1, -1,  1, -1, -1,  1, -2,  1];
t = [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
d = [1, 1, 3, 2, 2];
capacity = 9;

t_start = [ 0,  0,  0,  0,  0];
t_end =   [10, 10, 10, 10, 10];

startN = 1;
endN = 1;

[path, cost] = vrptw_neg_path(E, c, t, startN, endN, d, capacity, t_start, t_end);
expected_path1 = [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0];
expected_cost1 = 0;

assert(norm(expected_path1 - path(1, :)) == 0, 'Subproblem test 4 failed! One of the paths is invalid!');
assert(expected_cost1 - cost(1) == 0, 'Subproblem test 4 failed! One of the costs is invalid!');