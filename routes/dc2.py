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


def grow_colony_weight(colony, generations):
    colony = [int(d) for d in colony]  # Convert string to a list of integers
    
    if generations <= 10:
        for _ in range(generations):
            weight = sum(colony)  # Calculate the weight of the current colony
            new_colony = []  # Create a new list for the next generation

            for i in range(len(colony) - 1):
                a = colony[i]
                b = colony[i + 1]
                signature = calculate_signature(a, b)
                new_digit = (weight + signature) % 10
                
                new_colony.append(a)  # Append the current digit
                new_colony.append(new_digit)  # Append the new digit
            
            new_colony.append(colony[-1])  # Add the last digit of the current colony
            colony = new_colony  # Update the colony for the next generation
        
        return sum(colony)  # Return the final weight of the colony


@app.route('/digital-colony', methods=['POST'])
def digital_colony():
    data = request.get_json()
    logging.info("Data received for evaluation: {}".format(data))
    
    results = []
    
    for item in data:
        generations = item['generations']
        colony = item['colony']
        
        grown_colony = grow_colony(colony, generations)
        
        final_weight = sum(int(c) for c in grown_colony)
        
        results.append(str(final_weight))
    
    logging.info("Results computed: {}".format(results))
    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug=True)
