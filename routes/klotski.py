import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

# Function to move the pieces based on the moves string
def move_pieces(board, moves):
    # Convert the board string to a list for easier manipulation
    board_list = list(board)
    
    # Get the width of the board (assuming fixed width for Klotski)
    width = 4
    empty_index = board_list.index('@')  # Find the index of the empty space

    # Define the direction mappings
    directions = {
        'N': -width,  # Move up
        'S': width,   # Move down
        'E': 1,       # Move right
        'W': -1       # Move left
    }

    # Process moves in pairs
    for i in range(0, len(moves), 2):
        direction = moves[i]       # The first character of the pair (direction)
        block = moves[i + 1]      # The second character of the pair (block to move)

        # Find the current index of the block
        block_index = board_list.index(block)

        # Calculate the index of the target position for the block
        target_index = block_index + directions[direction]

        # Ensure that the block can move to the empty space
        if target_index == empty_index:
            # Swap the empty space with the block
            board_list[empty_index], board_list[block_index] = board_list[block_index], board_list[empty_index]
            # Update the index of the empty space
            empty_index = block_index  # Update to the new empty index

    # Convert the list back to a string
    return ''.join(board_list)

@app.route('/klotski', methods=['POST'])
def klotski():
    data = request.json
    result_boards = []
    
    for item in data:
        board = item["board"]
        moves = item["moves"]
        
        # Process the moves on the board and get the resultant board
        result_board = move_pieces(board, moves)
        result_boards.append(result_board)
    
    return jsonify(result_boards)

if __name__ == '__main__':
    app.run(debug=True)
