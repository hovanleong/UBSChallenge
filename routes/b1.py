from flask import Flask, request, jsonify
from collections import defaultdict, deque
import logging

from routes import app

logger = logging.getLogger(__name__)


@app.route('/bugfixer/p1', methods=['POST'])
def bug_fixer():
    data = request.get_json()
    results = []
    for entry in data:
        time = entry["time"]
        prerequisites = entry["prerequisites"]

        n = len(time)
        
        # Create a graph and indegree count
        graph = defaultdict(list)
        indegree = [0] * n
        
        for a, b in prerequisites:
            # Adjust for 0-based indexing
            graph[a - 1].append(b - 1)
            indegree[b - 1] += 1

        # Topological sorting using Kahn's algorithm
        queue = deque()
        for i in range(n):
            if indegree[i] == 0:
                queue.append(i)
        
        min_hours = [0] * n
        
        while queue:
            project = queue.popleft()
            
            # The minimum time to finish this project
            min_hours[project] += time[project]
            
            for neighbor in graph[project]:
                # Decrease indegree and check if it can be added to the queue
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
                    
                # Update the minimum hours required for the dependent project
                min_hours[neighbor] = max(min_hours[neighbor], min_hours[project])
        
        # The final result is the maximum time required to finish all projects
        results.append([min_hours[i] + time[i] for i in range(n)])
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
