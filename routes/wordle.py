import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

WORD_LIST = ['slate', 'lucky', 'maser', 'gapes', 'wages', 'apple', 'brick', 'train', 'plate', 'crane']

def get_next_guess(guess_history, evaluation_history):
    possible_words = [word for word in WORD_LIST if word not in guess_history]
    return possible_words[0] if possible_words else None

@app.route('/wordle-game', methods=['POST'])
def evaluate():
    data = request.get_json()
    logging.info("Data sent for evaluation: {}".format(data))

    guess_history = data.get("guessHistory", [])
    evaluation_history = data.get("evaluationHistory", [])

    next_guess = get_next_guess(guess_history, evaluation_history)
    
    if next_guess is None:
        logging.error("No more possible words to guess.")
        return json.dumps({"error": "No more possible words to guess"}), 400

    logging.info("Next guess: {}".format(next_guess))
    return json.dumps({"guess": next_guess})
