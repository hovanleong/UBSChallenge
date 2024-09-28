import json
import logging

from flask import request

from routes import app

from constants.tourist import TRAVELLING_TIME, TRAIN_LINES
from heapq import heappop, heappush

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the level of the logger

# Create a file handler
file_handler = logging.FileHandler('app.tourist.log')  # Name of the file where logs will be written
file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)  # Apply the formatter to the handler

# Add the file handler to the logger
logger.addHandler(file_handler)

# Graph construction function
def build_graph():
    # Step 1: Collect all unique stations
    all_stations = set()
    for stations in TRAIN_LINES.values():
        all_stations.update(stations)

    # Step 2: Create mappings from station name to index and vice versa
    station_to_index = {station: idx for idx, station in enumerate(sorted(all_stations))}
    index_to_station = {idx: station for station, idx in station_to_index.items()}

    # Step 3: Initialize the adjacency list
    graph = {i: [] for i in station_to_index.values()}  # Each node points to a list of tuples (neighbor, cost)
    
    for line, stations in TRAIN_LINES.items():
        travel_time = TRAVELLING_TIME.get(line)
        if not travel_time:
            continue
        
        prev_station = None
        for station in stations:
            station_idx = station_to_index[station]
            if prev_station is not None:
                prev_station_idx = station_to_index[prev_station]

                # Check if connection already exists and update if the new travel time is smaller
                existing_connection = next(((neighbor, cost) for neighbor, cost in graph[prev_station_idx] if neighbor == station_idx), None)
                
                if existing_connection:
                    # Update the connection with the smaller travel time
                    current_cost = existing_connection[1]
                    if travel_time < current_cost:
                        # Update both directions (prev -> current and current -> prev)
                        graph[prev_station_idx] = [(neighbor, cost if neighbor != station_idx else travel_time) for neighbor, cost in graph[prev_station_idx]]
                        graph[station_idx] = [(neighbor, cost if neighbor != prev_station_idx else travel_time) for neighbor, cost in graph[station_idx]]
                else:
                    # If no existing connection, add the new one
                    graph[prev_station_idx].append((station_idx, travel_time))
                    graph[station_idx].append((prev_station_idx, travel_time))
                    
            prev_station = station

    return graph, station_to_index, index_to_station

# Build the graph, station-to-index mappings, and index-to-station mappings
graph, station_to_index, index_to_station = build_graph()

# Function to find all paths between two stations under a cost threshold
def find_all_paths(graph, start, end, max_cost):
    """
    Find all paths between start and end that are within the given max_cost.
    """
    def dfs(current, end, visited, current_path, current_cost):
        # Debugging statement to trace DFS calls
        # logger.debug(f"DFS visiting node {current} with current path: {current_path} and cost: {current_cost}")
        
        if current_cost > max_cost:
            return
        if current == end:
            # Avoid logging the same path multiple times
            path_tuple = tuple(current_path)
            if path_tuple not in unique_paths:
                unique_paths.add(path_tuple)
                logger.info(f"Path found: {current_path} with cost {current_cost}")
                all_paths.append((list(current_path), current_cost))
            return
        
        # Explore neighbors
        for neighbor, travel_cost in graph[current]:
            if neighbor not in visited:  # Avoid revisiting nodes
                visited.add(neighbor)
                current_path.append(neighbor)
                
                # Recurse deeper into the graph
                dfs(neighbor, end, visited, current_path, current_cost + travel_cost)
                
                # Backtrack: remove the last node added to the path
                current_path.pop()
                visited.remove(neighbor)

    all_paths = []
    unique_paths = set()  # Set to store unique paths
    visited = set([start])  # Initialize the visited set with the start node
    dfs(start, end, visited, [start], 0)  # Start DFS with the start node
    
    return all_paths

# TSP between key stations using dynamic programming with bitmasking
def tsp_between_key_stations(key_stations, paths_between_keys, satisfaction, extra_cost, max_cost, start_idx):
    n = len(key_stations)
    key_station_indices = {station: i for i, station in enumerate(key_stations)}
    
    # DP table: dp[mask][i] = tuple (max_satisfaction, total_cost, visited_stations_set)
    # `visited_stations_set` keeps track of all stations (key and minor) visited from start to key station `i`
    dp = [[(-float('inf'), float('inf'), set())] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]  # To reconstruct the path
    
    # Base case: starting from the starting station with satisfaction and cost
    dp[1 << start_idx][start_idx] = (satisfaction[start_idx], 0, {key_stations[start_idx]})  # Start at start_idx
    
    # Fill DP table
    for mask in range(1 << n):
        for u in range(n):
            if mask & (1 << u):  # If u is in the current mask (visited)
                for v in range(n):
                    if mask & (1 << v) == 0:  # If v is not in the mask (unvisited)
                        if (key_stations[u], key_stations[v]) in paths_between_keys:
                            for path, path_cost in paths_between_keys[(key_stations[u], key_stations[v])]:
                                new_cost = dp[mask][u][1] + path_cost + extra_cost[v]
                                new_satisfaction = dp[mask][u][0] + satisfaction[v]
                                new_mask = mask | (1 << v)
                                
                                # Collect all stations on the path from the start point to v
                                # This includes the stations visited along all previous paths plus the current path
                                path_stations = set(path)  # Stations in the current path u -> v
                                cumulative_stations = dp[mask][u][2].union(path_stations)  # Include all previously visited stations
                                
                                # Check if any stations have already been visited
                                if key_stations[v] not in cumulative_stations:  # Ensure the key station `v` itself isn't revisited
                                    cumulative_stations.add(key_stations[v])  # Add the current key station `v` to the visited set
                                    
                                    # Update only if no duplicates and the new cost is within the budget
                                    if new_cost <= max_cost and new_satisfaction > dp[new_mask][v][0]:
                                        dp[new_mask][v] = (new_satisfaction, new_cost, cumulative_stations)
                                        parent[new_mask][v] = u
    
    # Find the best path that visits all key stations, returns to the start, and maximizes satisfaction
    final_mask = (1 << n) - 1  # All stations visited
    best_satisfaction = -float('inf')
    best_cost = float('inf')
    last_station = -1
    
    # Ensure we return to the start station
    for i in range(n):
        if i != start_idx and (key_stations[i], key_stations[start_idx]) in paths_between_keys:
            return_path_cost = paths_between_keys[(key_stations[i], key_stations[start_idx])][0][1]
            total_cost = dp[final_mask][i][1] + return_path_cost
            total_satisfaction = dp[final_mask][i][0]
            
            # Only consider this path if it stays within the max_cost
            if total_cost <= max_cost and total_satisfaction > best_satisfaction:
                best_satisfaction = total_satisfaction
                best_cost = total_cost
                last_station = i
    
    # Reconstruct the path
    mask = final_mask
    path = []
    
    while last_station != -1:
        path.append(key_stations[last_station])
        next_station = parent[mask][last_station]
        mask ^= (1 << last_station)
        last_station = next_station
    
    # Add the start station to the beginning and the end
    path.reverse()  # Since we built the path backwards
    path = [key_stations[start_idx]] + path + [key_stations[start_idx]]
    
    return best_cost, best_satisfaction, path

# Function to solve the entire problem by finding paths between key stations and concatenating them
def solve_tour_with_key_stations(graph, locations, max_cost, start_station):

    logger.info(type(station_to_index))
    start_idx = station_to_index[start_station]

    key_stations = [station_to_index[station_name] for station_name in locations.keys()]
    satisfaction = {station_to_index[station_name]: satisfaction for station_name, (satisfaction, extra_cost) in locations.items()}
    extra_cost = {station_to_index[station_name]: extra_cost for station_name, (satisfaction, extra_cost) in locations.items()}
    
    # Find all paths between each pair of key stations
    paths_between_keys = {}
    for i in range(len(key_stations)):
        for j in range(i + 1, len(key_stations)):
            start, end = key_stations[i], key_stations[j]
            logger.info(f'{start}, {end}')
            all_paths = find_all_paths(graph, start, end, max_cost)
            if all_paths:
                paths_between_keys[(start, end)] = all_paths
                paths_between_keys[(end, start)] = [(path[::-1], cost) for path, cost in all_paths]  # Add reverse paths
    
    # Solve the TSP between key stations with the start fixed
    best_cost, best_path = tsp_between_key_stations(key_stations, paths_between_keys, satisfaction, extra_cost, max_cost, start_idx)
    
    return best_cost, best_path

@app.route('/tourist', methods=['POST'])
def tourist():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result = solve_tour_with_key_stations(graph, data['locations'], data['timeLimit'], data['startingPoint'])
    logging.info("My result :{}".format(result))
    return json.dumps(result)
