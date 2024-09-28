import json
import logging

from flask import Flask, request, jsonify

from routes import app

# Load your word list
WORD_LIST = []
def load_words_from_file(file_path):
    with open(file_path, 'r') as file:
        words = [line.strip() for line in file.readlines()]
    return words

# Usage
file_path = 'words.txt'  # Replace with your actual file path
WORD_LIST = load_words_from_file(file_path)



def filter_words(guess_history, evaluation_history):
    confirmed = [''] * 5
    possible = {}
    letters = [5] * 26
    n = len(guess_history)
    for i in range(n):
        g = guess_history[i]
        e = evaluation_history[i]
        for j in range(5):
            if e[j] == 'O':
                confirmed[j] = g[j]
            elif e[j] == 'X':
                if possible.get(g[j]) == None:
                    possible[g[j]] = [i for i in range(5) if i != j]
                else:
                    if j in possible[g[j]]:
                        possible[g[j]].remove(j)  
            elif e[j] == '-':
                if g[j] not in confirmed and g[j] not in possible:    
                    letters[ord(g[j]) - ord('a')] = 0
           

    res = ''
    print(confirmed)
    print(possible)
    print(letters)
    for word in WORD_LIST:
        match = True
        avail_index = [0, 1, 2, 3, 4]
        
        # Check against confirmed letters
        for i in range(5):
            if confirmed[i] != '':
                if word[i] != confirmed[i]:
                    match = False
                    break  # Word does not match confirmed letter
                else:
                    avail_index.remove(i)
                    if word[i] in possible:
                        del possible[word[i]]
        
        if not match:
            continue  # Skip this word if it doesn't match confirmed letters
        # Check against possible letters and their positions
        possible_duplicate = possible.copy()
        for i in avail_index:
            for k in possible:
                if word[i] == k:
                    if possible[k] != None and i in possible[k]:
                        if k in possible_duplicate:
                            del possible_duplicate[k]
                    
        if possible_duplicate:
            continue
        
        # Check against excluded letters
        for j in range(26):
            if word.count(chr(j + ord('a'))) > letters[j]:
                match = False
                break  # Word contains an excluded letter
        # If all conditions are satisfied, add to valid guesses
        if match:
            res = word
            break
    if res == '':
        return WORD_LIST[0]
    return res

@app.route('/wordle-game', methods=['POST'])
def wordle_game():
    data = request.json
    guess_history = data.get("guessHistory", [])
    evaluation_history = data.get("evaluationHistory", [])
    logging.info("data sent for evaluation {}".format(data))
    # First guess, return "slate"
    if not guess_history:
        return jsonify({"guess": "slate"})

    # Filter possible words based on the history
    res = filter_words(guess_history, evaluation_history)
    logging.info("My result :{}".format(res))

    return jsonify({"guess": res})

if __name__ == '__main__':
    app.run(debug=True)
