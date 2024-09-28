import math

from flask import Flask, request, jsonify

from routes import app

def calculate_efficiency(monsters):
    res = 0
    n = len(monsters)

    if n == 0:
        return 0
    
    curr_min = monsters[0]
    curr_max = monsters[0]
    
    for i in range(1, n):
        if monsters[i] < curr_min:
            curr_min = monsters[i]
        if monsters[i] > curr_max:
            curr_max = monsters[i]
        if monsters[i] < curr_max:
            diff = curr_max - curr_min
            res += diff
            curr_min = math.inf
            curr_max = -math.inf
    if curr_min != math.inf and curr_max != -math.inf and curr_max - curr_min > 0:
        res += curr_max - curr_min
    return res


    # n = len(monsters)
    # if n == 0:
    #     return 0

    # # Initialize dp array to store maximum profit at each time step
    # # dp[i][0] represents max profit if we don't attack at step i
    # # dp[i][1] represents max profit if we attack at step i
    # dp = [[0 for _ in range(n + 1)] for _ in range(n + 1)]

    # # Fill dp array from right to left
    # for i in range(n - 1, -1, -1):
    #     # Option 1: Don't attack at this step
    #     max_res = -math.inf
    #     for j in range(i + 1, n):
    #         if dp[j][j - i] > max_res:
    #             max_res = dp[j][j - i]
    #     if max_res == - math.inf:
    #         dp[i][0] = 0
    #     else:
    #         dp[i][0] = max_res

    #     # Option 2: Attack at this step
    #     # We can only attack if we didn't attack in the previous step
    #     # The cost of preparation is the number of monsters at the previous time step
    #     for j in range(i):
    #         dp[i][j] = monsters[i] - monsters[j] + dp[i + 1][0]

    # res = -math.inf
    # for i in range(n):
    #     res = max(res, dp[0][i])
    # return res        

@app.route('/efficient-hunter-kazuma', methods=['POST'])
def efficient_hunter_kazuma():
    data = request.get_json()
    results = []

    for entry in data:
        monsters = entry["monsters"]
        efficiency = calculate_efficiency(monsters)
        results.append({"efficiency": efficiency})
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
