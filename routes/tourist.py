import json
import logging

from flask import request

from routes import app

from constants.tourist import TRAVELLING_TIME, TRAIN_LINES
from collections import deque

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

def build_graph():
    graph = {}  # This will store the adjacency list
    
    for line, stations in TRAIN_LINES.items():
        # Iterate through each station in the train line and connect it to its neighbors

        travel_time = TRAVELLING_TIME.get(line)
        if not travel_time:
            continue

        prev_station = None
        for station in stations:
            if station not in graph:
                graph[station] = []
            if prev_station:
                graph[prev_station].append((station, travel_time))
                graph[station].append((prev_station, travel_time))
            prev_station = station
    
    return graph

graph = build_graph()

import heapq
from collections import defaultdict

def dijkstra(graph, start):
    dist = defaultdict(lambda: float('inf'))
    dist[start] = 0
    pq = [(0, start)]  # (distance, station)
    prev = {start: None}  # Track the previous station to reconstruct the path

    while pq:
        current_dist, current_station = heapq.heappop(pq)

        if current_dist > dist[current_station]:
            continue

        for neighbor, travel_time in graph[current_station]:
            new_dist = current_dist + travel_time
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current_station  # Update the previous station
                heapq.heappush(pq, (new_dist, neighbor))

    # Reconstruct full paths
    paths = {station: [] for station in dist}
    for station in dist:
        current = station
        while current is not None:
            paths[station].append(current)
            current = prev[current]
        paths[station].reverse()  # Reverse to get the correct order

    return dist, paths

def get_shortest_paths(graph, key_stations):
    shortest_paths = {}
    full_paths = {}  # Store full paths between key stations

    for station in key_stations:
        dist, paths = dijkstra(graph, station)
        shortest_paths[station] = dist
        full_paths[station] = paths

    return shortest_paths, full_paths

def maximize_satisfaction_dp(locations, graph, starting_point, time_limit):
    # Get key locations (stations with satisfaction)
    
    # Precompute shortest paths and full paths between key stations
    shortest_paths, full_paths = get_shortest_paths(graph, locations)
    
    # Map stations to indices for bitmasking
    station_idx = {station: idx for idx, station in enumerate(locations)}
    idx_station = {idx: station for station, idx in station_idx.items()}
    n = len(locations)
    
    # Dynamic Programming table: dp[mask][i] = (max_satisfaction, remaining_time)
    dp = [[(-float('inf'), 0)] * n for _ in range(1 << n)]
    prev_station = [[-1] * n for _ in range(1 << n)]  # To store the previous station for backtracking
    
    start_idx = station_idx[starting_point]
    dp[1 << start_idx][start_idx] = (0, time_limit)  # Start at the starting point with time limit
    
    # Iterate over all possible masks (sets of visited stations)
    for mask in range(1 << n):
        for u in range(n):  # Station u
            if dp[mask][u][0] == -float('inf'):  # Skip invalid states
                continue
            
            current_satisfaction, remaining_time = dp[mask][u]
            current_station = idx_station[u]
            
            # Try to go to all other unvisited stations
            for v in range(n):
                if mask & (1 << v):  # Skip if station v has already been visited
                    continue
                
                next_station = idx_station[v]
                travel_time = shortest_paths[current_station][next_station]
                
                if remaining_time - travel_time >= 0:  # Check if there's enough time to reach the next station
                    satisfaction, time_at_station = locations.get(next_station, (0, 0))
                    new_mask = mask | (1 << v)  # Mark the station as visited
                    new_remaining_time = remaining_time - travel_time - time_at_station
                    
                    # Only update DP table if there's enough time to return to the start
                    return_to_start_time = shortest_paths[next_station][starting_point]
                    if new_remaining_time - return_to_start_time >= 0:  # Ensure enough time to return to start
                        # Ensure we have time left to return
                        if dp[new_mask][v][0] < current_satisfaction + satisfaction and new_remaining_time >= 0:
                            dp[new_mask][v] = (current_satisfaction + satisfaction, new_remaining_time)
                            prev_station[new_mask][v] = u  # Store the previous station
    
    # Find the maximum satisfaction when returning to the starting point
    best_satisfaction = 0
    best_final_state = (0, 0)
    
    for mask in range(1 << n):
        for u in range(n):
            if dp[mask][u][0] > -float('inf'):  # Valid state
                travel_time_back = shortest_paths[idx_station[u]][starting_point]
                if dp[mask][u][1] - travel_time_back >= 0:  # Ensure enough time to return
                    if dp[mask][u][0] > best_satisfaction:
                        best_satisfaction = dp[mask][u][0]
                        best_final_state = (mask, u)

    # Reconstruct the path and the total travel time
    best_mask, best_final_station = best_final_state
    key_path = []
    total_travel_time = 0
    current_station = best_final_station
    
    # Backtrack from the final station
    while best_mask != 0:
        key_path.append(idx_station[current_station])
        next_station = prev_station[best_mask][current_station]
        
        # Add travel time between current_station and next_station
        if next_station != -1:
            total_travel_time += shortest_paths[idx_station[current_station]][idx_station[next_station]]
        
        best_mask ^= (1 << current_station)  # Remove current station from mask
        current_station = next_station
    
    key_path.reverse()  # Reverse to get the correct order
    
    # Finally, add the time to return to the starting point
    total_travel_time += shortest_paths[idx_station[best_final_station]][starting_point]
    key_path.append(starting_point)  # Return to the starting point

    # Reconstruct the full path using the full_paths dictionary
    full_path = []
    for i in range(len(key_path) - 1):
        current_station = key_path[i]
        next_station = key_path[i + 1]
        full_path += full_paths[current_station][next_station][:-1]  # Append all but the last station to avoid duplicates
    full_path.append(starting_point)  # Add the final station (starting point)

    return {"key_path": key_path, "full_path": full_path, "satisfaction": best_satisfaction, "total_travel_time": total_travel_time}


# # Dijkstra's algorithm to find the shortest path from a start station to all others
# def dijkstra(graph, start):
#     dist = defaultdict(lambda: float('inf'))
#     dist[start] = 0
#     pq = [(0, start)]  # (distance, station)
    
#     while pq:
#         current_dist, current_station = heapq.heappop(pq)
        
#         if current_dist > dist[current_station]:
#             continue
        
#         for neighbor, travel_time in graph[current_station]:
#             new_dist = current_dist + travel_time
#             if new_dist < dist[neighbor]:
#                 dist[neighbor] = new_dist
#                 heapq.heappush(pq, (new_dist, neighbor))
    
#     return dist

# # Get shortest paths between key stations using Dijkstra's algorithm
# def get_shortest_paths(graph, key_stations):
#     shortest_paths = {}
    
#     for station in key_stations:
#         shortest_paths[station] = dijkstra(graph, station)
    
#     return shortest_paths

# def maximize_satisfaction_dp(locations, graph, starting_point, time_limit):
#     # Get key locations (stations with satisfaction)
    
#     # Precompute shortest paths between key stations
#     shortest_paths = get_shortest_paths(graph, locations)
    
#     # Map stations to indices for bitmasking
#     station_idx = {station: idx for idx, station in enumerate(locations)}
#     idx_station = {idx: station for station, idx in station_idx.items()}
#     n = len(locations)
    
#     # Dynamic Programming table: dp[mask][i] = (max_satisfaction, remaining_time)
#     dp = [[(-float('inf'), 0)] * n for _ in range(1 << n)]
#     prev_station = [[-1] * n for _ in range(1 << n)]  # To store the previous station for backtracking
    
#     start_idx = station_idx[starting_point]
#     dp[1 << start_idx][start_idx] = (0, time_limit)  # Start at the starting point with time limit
    
#     # Iterate over all possible masks (sets of visited stations)
#     for mask in range(1 << n):
#         for u in range(n):  # Station u
#             if dp[mask][u][0] == -float('inf'):  # Skip invalid states
#                 continue
            
#             current_satisfaction, remaining_time = dp[mask][u]
#             current_station = idx_station[u]
            
#             # Try to go to all other unvisited stations
#             for v in range(n):
#                 if mask & (1 << v):  # Skip if station v has already been visited
#                     continue
                
#                 next_station = idx_station[v]
#                 travel_time = shortest_paths[current_station][next_station]
                
#                 if remaining_time - travel_time >= 0:  # Check if there's enough time to reach the next station
#                     satisfaction, time_at_station = locations.get(next_station, (0, 0))
#                     new_mask = mask | (1 << v)  # Mark the station as visited
#                     new_remaining_time = remaining_time - travel_time - time_at_station
                    
#                     # Only update DP table if there's enough time to return to the start
#                     return_to_start_time = shortest_paths[next_station][starting_point]
#                     if new_remaining_time - return_to_start_time >= 0:  # Ensure enough time to return to start
#                         # Ensure we have time left to return
#                         if dp[new_mask][v][0] < current_satisfaction + satisfaction and new_remaining_time >= 0:
#                             dp[new_mask][v] = (current_satisfaction + satisfaction, new_remaining_time)
#                             prev_station[new_mask][v] = u  # Store the previous station
    
#     # Find the maximum satisfaction when returning to the starting point
#     best_satisfaction = 0
#     best_final_state = (0, 0)
    
#     for mask in range(1 << n):
#         for u in range(n):
#             if dp[mask][u][0] > -float('inf'):  # Valid state
#                 travel_time_back = shortest_paths[idx_station[u]][starting_point]
#                 if dp[mask][u][1] - travel_time_back >= 0:  # Ensure enough time to return
#                     if dp[mask][u][0] > best_satisfaction:
#                         best_satisfaction = dp[mask][u][0]
#                         best_final_state = (mask, u)

#     # Reconstruct the path and the total travel time
#     best_mask, best_final_station = best_final_state
#     path = []
#     total_travel_time = 0
#     current_station = best_final_station
    
#     # Backtrack from the final station
#     while best_mask != 0:
#         path.append(idx_station[current_station])
#         next_station = prev_station[best_mask][current_station]
        
#         # Add travel time between current_station and next_station
#         if next_station != -1:
#             total_travel_time += shortest_paths[idx_station[current_station]][idx_station[next_station]]
        
#         best_mask ^= (1 << current_station)  # Remove current station from mask
#         current_station = next_station
    
#     path.reverse()  # Reverse to get the correct order
    
#     # Finally, add the time to return to the starting point
#     total_travel_time += shortest_paths[idx_station[best_final_station]][starting_point]
#     path.append(starting_point)  # Return to the starting point
    
#     return {"path": path, "satisfaction": best_satisfaction, "total_travel_time": total_travel_time}


@app.route('/tourist', methods=['POST'])
def tourist():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result = maximize_satisfaction_dp(data['locations'], graph, data['startingPoint'], data['timeLimit'])
    logging.info("My result :{}".format(result))
    return json.dumps(result)
