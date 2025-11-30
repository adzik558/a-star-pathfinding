import osmnx as ox
import networkx as nx
from math import sqrt
from collections import deque
import heapq
import time
from math import radians, cos, sin, asin, sqrt

def great_circle_vec(lat1, lon1, lat2, lon2):
    """
    Oblicza odległość wielkiego koła w metrach między dwoma punktami.
    """
    R = 6371000  # promień Ziemi w metrach
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def get_heuristic_func(u, v, G, heuristic_type="euklidesowa"):
    u_node = G.nodes[u]
    v_node = G.nodes[v]

    if heuristic_type == "euklidesowa":
        return great_circle_vec(u_node['y'], u_node['x'], v_node['y'], v_node['x'])
    elif heuristic_type == "manhattan":
        dx = great_circle_vec(u_node['y'], u_node['x'], u_node['y'], v_node['x'])
        dy = great_circle_vec(u_node['y'], u_node['x'], v_node['y'], u_node['x'])
        return 1.2 * (dx + dy)
    return 0.0

def find_path(G, start_node, end_node, algorithm_name, heuristic="euklidesowa"):
    time_components = {}
    visited_count = 0
    path = None
    parents = {start_node: None}

    t0 = time.perf_counter()
    t1 = time.perf_counter()
    time_components['init_time'] = t1 - t0

    if algorithm_name in ["A*", "Dijkstra"]:
        queue = [(0.0, 0.0, start_node)]
        costs = {start_node: 0.0}
        visited = set()

        t0 = time.perf_counter()
        while queue:
            priority, cost, u = heapq.heappop(queue)
            if u in visited:
                continue
            visited.add(u)
            visited_count += 1

            if u == end_node:
                break

            for v, data in G.adj[u].items():
                edge_cost = data.get("length", 1)
                new_cost = cost + edge_cost

                if v not in costs or new_cost < costs[v]:
                    costs[v] = new_cost
                    new_priority = new_cost
                    if algorithm_name == "A*":
                        new_priority += get_heuristic_func(v, end_node, G, heuristic)
                    heapq.heappush(queue, (new_priority, new_cost, v))
                    parents[v] = u

        t1 = time.perf_counter()
        time_components['loop_time'] = t1 - t0

    elif algorithm_name == "BFS":
        queue = deque([start_node])
        visited = set([start_node])

        t0 = time.perf_counter()
        while queue:
            u = queue.popleft()
            visited_count += 1

            if u == end_node:
                break

            for v in G.neighbors(u):
                if v not in visited:
                    parents[v] = u
                    visited.add(v)
                    queue.append(v)
        t1 = time.perf_counter()
        time_components['loop_time'] = t1 - t0

    else:
        raise ValueError("Nieznany algorytm: " + algorithm_name)

    t0 = time.perf_counter()
    if end_node in parents:
        path = [end_node]
        while path[-1] != start_node:
            path.append(parents[path[-1]])
        path.reverse()
    t1 = time.perf_counter()
    time_components['reconstruction_time'] = t1 - t0

    return path, visited_count, time_components
