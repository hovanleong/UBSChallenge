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
    entry = request.get_json()
    results = []

    dictionary = entry["dictionary"]
    mistypes = entry["mistypes"]
    
    words_by_length = {}
    for word in dictionary:
        if len(word) in words_by_length:
            words_by_length[len(word)].append(word)
        else:
            words_by_length[len(word)] = [word]

    corrections = []

    # For each mistyped word, find the corresponding correct word
    for mistype in mistypes:
        possible_corrections = words_by_length[len(mistype)]
        for word in possible_corrections:
            if compare(mistype, word):
                corrections.append(word)

    results.append({'corrections': corrections})
    
    return jsonify(results)