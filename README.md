





# COG-LO Services

## VRPTW (MATLAB) Service

### Input Data Structures

`m` ... stevilo edge-ov
`k` ... stevilo vozil

Graf: incidence matrika
```
E = [
    [-1, -1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0]
    [ 1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  1, -1, -1, -1,  1,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  0,  1],
    [ 0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1, -1]
];
```



Cene poti: k x m matrika, vsaka vrstica predstavlja vozilo, stolpec predtsavlja povezavo, (i,j)-ti element pove koliko stane j-ta pot, ce jo prevozi vozilo k
```
C_edge = [
    [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1],
    [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1]
];
```

Cas poti: vektor dolzine m, ki pove koliko casa rabis, da prevozis vsako povezavo
```
edge_time_vec = [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1];
```

Vektor odpiralnih in vektor zapiralnih casov: Za vsak node pove, katero uro se odpre/zapre (vozila vedno startajo ob casu 0).
```
t_start_vec = [0, 0, 0, 0, 0];
t_end_vec = [10, 10, 10, 10, 10];
```

Distribution vector: pove koliko parcelov odloziti v vsakem node-u
```
distrib_vec = [0, 4, 3, 4, 3];
```

Capacity vector: kapaciteta vozil
```
capacity_vec = [10, 10];
```

Start vektor: za vsako vozilo pove v katerem node-u zacne
End vektor: za vsako vozilo pove v katerem node-u konca
```
start_vec = [1, 1];
end_vec = [1, 1];
```

### REST API

The HTTP API is running on the COG-LO machine on port
`4505`. Here is an example of the HTTP request:
```
POST /api/vrptw
{
    'incidenceMat': [
        [-1, -1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0],
        [ 1,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  1, -1, -1, -1,  1,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  1,  0, -1, -1,  0,  0,  1],
        [ 0,  1,  0,  0,  0,  0,  1,  0,  1, -1, -1, -1]
    ],
    'costMat': [
        [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1],
        [ 6,  1,  6,  6,  6,  1,  1,  1,  1,  1,  1,  1]
    ],
    'edgeTimeV': [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1],
    'startV': [1, 1],
    'endV': [1, 1],
    'nodeDistributionV': [0, 4, 3, 4, 3],
    'vehicleCapacityV': [10, 10],
    'nodeOpenV': [0, 0, 0, 0, 0],
    'nodeCloseV': [10, 10, 10, 10, 10]
}
```

And an example of the response:
```
{
    "routes": [
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ],
    "cost": 17.0
}
```
