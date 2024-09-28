import json
import logging
from flask import Flask, request
from routes import app


def calculate_signature(a, b):
    if a == b:
        return 0
    elif a > b:
        return a - b
    else:
        return 10 - (b - a)

def grow_colony_weight(current_weight, counts, generations):
    for _ in range(generations):
        new_counts = [0] * 10
        for i in range(10):
            for j in range(10):
                if counts[i] > 0 and counts[j] > 0:
                    signature = calculate_signature(i, j)
                    new_digit = (current_weight + signature) % 10
                    new_counts[new_digit] += counts[i] * counts[j]
        current_weight = sum(counts) + sum(new_counts)  # Update weight
        counts = new_counts
    return current_weight

@app.route('/digital-colony', methods=['POST'])
def digital_colony():
    data = request.get_json()
    logging.info("Data received for evaluation: {}".format(data))
    
    results = []
    
    for item in data:
        generations = item['generations']
        colony = item['colony']
        
        # Initialize counts array
        counts = [0] * 10
        for char in colony:
            counts[int(char)] += 1
            
        initial_weight = sum(int(c) for c in colony)
        
        final_weight = grow_colony_weight(initial_weight, counts, generations)
        
        results.append(str(final_weight))
    
    logging.info("Results computed: {}".format(results))
    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug=True)