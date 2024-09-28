from flask import Flask, request, jsonify

from routes import app
from collections import defaultdict

def compare(s, t):
    n = len(s)
    count = 0
    for i in range(n):
        if s[i] != t[i]:
            count += 1
    return count == 1

@app.route('/the-clumsy-programmer', methods=['POST'])
def clumsy():
    data = request.get_json()
    results = []

    for entry in data:
        dictionary = entry["dictionary"]
        mistypes = entry["mistypes"]
        
        words_by_length = defaultdict(list)
        for word in dictionary:
            words_by_length[len(word)].append(word)

        corrections = []

        # For each mistyped word, find the corresponding correct word
        for mistype in mistypes:
            possible_corrections = words_by_length[len(mistype)]
            for word in possible_corrections:
                if compare(mistype, word):
                    corrections.append(word)

        results.append({'corrections': corrections})
    
    return jsonify(results)