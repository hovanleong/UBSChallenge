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

def grow_colony(colony, generations):
    for _ in range(generations):
        weight = sum(int(c) for c in colony)
        new_colony = []
        for i in range(len(colony) - 1):
            a = int(colony[i])
            b = int(colony[i + 1])
            signature = calculate_signature(a, b)
            new_digit = (weight + signature) % 10
            new_colony.append(colony[i])
            new_colony.append(str(new_digit))
        new_colony.append(colony[-1])  # Add the last digit
        colony = "".join(new_colony)
    return colony

def calculate_weight(colony):
    return sum(int(c) for c in colony)

@app.route('/digital-colony', methods=['POST'])
def digital_colony():
    data = request.get_json()
    logging.info("Data received for evaluation: {}".format(data))
    
    results = []

    for item in data:
        generations = item['generations']
        colony = item['colony']
        grown_colony = grow_colony(colony, generations)
        final_weight = calculate_weight(grown_colony)

        results.append(str(final_weight))
        

    logging.info("Results computed: {}".format(results))
    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug=True)