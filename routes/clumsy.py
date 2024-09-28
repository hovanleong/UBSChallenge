from flask import Flask, request, jsonify

from routes import app

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

        if dictionary:  # Ensure dictionary is not empty
            word_length = len(dictionary[0])

        corrections = []

        # For each mistyped word, find the first correct word (since one char is wrong)
        for mistype in mistypes:
            for word in dictionary:
                if compare(mistype, word):
                    corrections.append(word)
                    break  # Break out of the loop once a match is found

        results.append({"corrections": corrections})

    return jsonify(results)