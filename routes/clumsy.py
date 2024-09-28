from flask import Flask, request, jsonify

from routes import app

from joblib import Parallel, delayed

def compare(s, t):
    # We know s and t are the same length
    mismatch_count = 0
    for i in range(len(s)):
        if s[i] != t[i]:
            mismatch_count += 1
            # Exit early if there is more than 1 mismatch
            if mismatch_count > 1:
                return False
    return mismatch_count == 1  # Return True if exactly 1 mismatch

def find_correction(mistype, dictionary):
    # Find the first word in the dictionary that differs by exactly one character
    for word in dictionary:
        if compare(mistype, word):
            return word
    return None

@app.route('/the-clumsy-programmer', methods=['POST'])
def clumsy():
    data = request.get_json()
    results = []

    for entry in data:
        dictionary = entry["dictionary"]
        mistypes = entry["mistypes"]

        # Use parallel processing to speed up corrections search
        corrections = Parallel(n_jobs=-1)(delayed(find_correction)(mistype, dictionary) for mistype in mistypes)

        results.append({'corrections': corrections})

    return jsonify(results)