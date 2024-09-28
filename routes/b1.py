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

        def dfs(x):
            res = 0
            for n in graph[x]:
                res = max(res, dfs(n))
            return time[x] + res
        
        res = 0
        for i in range(n):
            if indegree[i] == 0:
                res = max(res, dfs(i))
        results.append(res)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
