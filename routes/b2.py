from flask import request, jsonify
import heapq

import logging

from routes import app
logger = logging.getLogger(__name__)


@app.route('/bugfixer/p2', methods=['POST'])
def max_bugsfixed():
    data = request.get_json()
    results = []
    
    for entry in data:
        bug_seq = entry["bugseq"]
        
        # Sort bugs by their limit
        bug_seq.sort(key=lambda x: x[1])  # Sort by limit
        
        total_time = 0
        min_heap = []  # Min-heap to keep track of the difficulties of fixed bugs
        count_bugs = 0
        
        for difficulty, limit in bug_seq:
            total_time += difficulty
            heapq.heappush(min_heap, -difficulty)
            count_bugs += 1
            
            # If total_time exceeds the limit, remove the most difficult bug
            if total_time > limit:
                # Remove the most difficult bug (max in min-heap)
                hardest_bug = -heapq.heappop(min_heap)
                total_time -= hardest_bug
                count_bugs -= 1  # Decrease the count as we can't fix this bug

        results.append(count_bugs)

    return jsonify(results)
