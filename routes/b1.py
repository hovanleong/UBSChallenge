import json
import logging
from collections import defaultdict, deque

from flask import request

from routes import app

@app.route('/bugfixer/p1', methods=['POST'])
def bug_fixer():
    data = request.json
    result = []

    for item in data:
        time = item["time"]
        prerequisites = item["prerequisites"]

        # Number of projects
        n = len(time)

        # Create a graph and in-degree count
        graph = defaultdict(list)
        in_degree = [0] * n
        project_times = [0] * n

        # Build the graph
        for a, b in prerequisites:
            graph[a - 1].append(b - 1)  # Convert to zero-indexed
            in_degree[b - 1] += 1

        # Initialize project times
        for i in range(n):
            project_times[i] = time[i]

        # Queue for processing projects with no prerequisites
        queue = deque()

        # Enqueue projects with no prerequisites
        for i in range(n):
            if in_degree[i] == 0:
                queue.append(i)

        # Topological sorting
        while queue:
            current = queue.popleft()

            # Process dependent projects
            for neighbor in graph[current]:
                # Update the time required to complete this project
                project_times[neighbor] = max(project_times[neighbor], project_times[current] + time[neighbor])

                # Decrease in-degree and check if ready to process
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # The result for this test case is the maximum time among all projects
        result.append(max(project_times))

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
