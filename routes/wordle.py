import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

confirmed = [''] * 5
possible = {}
letters = [True] * 26


@app.route('/wordle-game', methods=['POST'])
def wordle():
    data = request.get_json()
    guess_history = data["guessHistory"]
    evaluation_history = data["evaluationHistory"]

    n = len(guess_history)
    for i in range(n):
        g = guess_history[i]
        e = evaluation_history[i]
        for j in range(5):
            if e[j] == 'O':
                confirmed[j] = g[j]
            elif e[j] == 'X':
                if (possible.get(g[j]) == None):
                    possible[g[j]] = [i for i in range(5) if i != j]
                else:
                    if j in possible[g[j]]:
                        possible[g[j]] = possible[g[j]].remove(j)
            elif e[j] == '-':
                letters[ord(g[j]) - ord('a')] = False

    guess = [''] * 5
    for i in range(5):
        if confirmed[i] != '':
            guess[i] = confirmed[i]
    for i in range(5):
        if guess[i] == '':
            for k in possible:
                if i in possible[k]:
                    guess[i] = k
    for i in range(5):
        if guess[i] == '':
            for j in range(26):
                if letters[j]:
                    guess[i] = chr(j + ord('a'))
                    break
    return json.dumps({"guess": ''.join(guess)})
