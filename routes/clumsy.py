from flask import Flask, request, jsonify

from routes import app
from collections import defaultdict


def differs_by_one(word1, word2):
    return sum(1 for a, b in zip(word1, word2) if a != b) == 1

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
            correct_word = next((word for word in possible_corrections if differs_by_one(mistype, word)), None)
            corrections.append(correct_word if correct_word else mistype)

        results.append({'corrections': corrections})
    
    return jsonify(results)