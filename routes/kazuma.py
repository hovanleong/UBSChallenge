import math

from flask import Flask, request, jsonify

from routes import app

import math

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the level of the logger

# Create a file handler
file_handler = logging.FileHandler('app.kazuma.log')  # Name of the file where logs will be written
file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)  # Apply the formatter to the handler

# Add the file handler to the logger
logger.addHandler(file_handler)

def calculate_efficiency_dp(monsters):
    n = len(monsters)
    if n == 0:
        return 0  # No monsters, no profit
    
    # Initialize dp arrays
    # dp[i][0] -> Max profit up to time i if not attacking
    # dp[i][1] -> Max profit up to time i if attacking
    dp = [[0, 0] for _ in range(n)]

    # Base case for time 0
    dp[0][0] = 0 # uncharged
    dp[0][1] = -monsters[0] # charged

    # Fill the dp table
    for i in range(1, n):

        # If Kazuma is in rear at time i without charge, carry forward the max of the previous state (either attack or not attack)
        dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + monsters[i])

        # If Kazuma charges up at time i, subtract the cost of preparing
        dp[i][1] = max(dp[i - 1][1], dp[i - 1][0] - monsters[i])

    logger.info(dp)
    # The result is the maximum profit at the last time step, whether Kazuma attacks or not
    return max(dp[n - 1][0], dp[n - 1][1])

@app.route('/efficient-hunter-kazuma', methods=['POST'])
def efficient_hunter_kazuma():
    data = request.get_json()
    results = []

    for entry in data:
        monsters = entry["monsters"]
        efficiency = calculate_efficiency_dp(monsters)
        results.append({"efficiency": efficiency})
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
