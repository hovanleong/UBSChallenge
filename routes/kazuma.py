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
