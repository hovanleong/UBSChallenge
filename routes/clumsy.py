from flask import Flask, request, jsonify

from routes import app

import string

# Generate all variants of a word by changing one character
def generate_one_off_variants(word):
    variants = set()
    letters = string.ascii_lowercase
    for i in range(len(word)):
        for letter in letters:
            if letter != word[i]:
                # Replace character at position i with every possible letter
                variant = word[:i] + letter + word[i+1:]
                variants.add(variant)
    return variants

@app.route('/the-clumsy-programmer', methods=['POST'])
def clumsy():
    data = request.get_json()
    results = []

    for entry in data:
        dictionary = set(entry["dictionary"])  # Store the dictionary in a set for fast lookups
        mistypes = entry["mistypes"]
        corrections = []

        for mistype in mistypes:
            # Generate all possible variants of the mistyped word
            variants = generate_one_off_variants(mistype)
            # Check which variant exists in the dictionary
            for variant in variants:
                if variant in dictionary:
                    corrections.append(variant)
                    break  # Stop as soon as a correction is found

        results.append({'corrections': corrections})

    return jsonify(results)