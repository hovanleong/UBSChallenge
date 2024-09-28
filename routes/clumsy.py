from flask import Flask, request, jsonify

from routes import app

import Levenshtein

def compare(s, t):
    return Levenshtein.distance(s, t) == 1

@app.route('/the-clumsy-programmer', methods=['POST'])
def clumsy():
    data = request.get_json()
    results = []

    for entry in data:
        dictionary = entry["dictionary"]
        mistypes = entry["mistypes"]

        corrections = []

        # For each mistyped word, find the first correct word (since one char is wrong)
        for mistype in mistypes:
            for word in dictionary:
                if compare(mistype, word):
                    corrections.append(word)
                    break  # Break out of the loop once a match is found

        results.append({"corrections": corrections})

    return jsonify(results)