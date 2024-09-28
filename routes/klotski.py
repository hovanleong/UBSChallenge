import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

# Function to move the pieces based on the moves string
def move_pieces(board, moves):
    # Get the width of the board (assuming fixed width for Klotski)
    width = 4

    # Create a dictionary to hold the coordinates of each block
    block_positions = {block: (i // width, i % width) for i, block in enumerate(board)}
    empty_position = block_positions['@']  # Get the position of the empty space

    # Define the direction mappings
    directions = {
        'N': (-1, 0),  # Move up
        'S': (1, 0),   # Move down
        'E': (0, 1),   # Move right
        'W': (0, -1)   # Move left
    }

    # Process moves in pairs
    for i in range(0, len(moves), 2):
        direction = moves[i + 1]       # The first character of the pair (direction)
        block = moves[i]      # The second character of the pair (block to move)

        for block in block_positions:
            # Get the current position of the block
            block_position = block_positions[block]
            target_position = (block_position[0] + directions[direction][0], 
                            block_position[1] + directions[direction][1])

            # Check if the target position is valid and is the empty space
            if target_position == empty_position:
                # Swap the block and the empty space in the dictionary
                block_positions[block], block_positions['@'] = empty_position, block_position

                # Update the empty position
                empty_position = block_position

    # Build the resultant board string from the block positions
    result_board = [''] * len(board)
    for block, position in block_positions.items():
        index = position[0] * width + position[1]  # Convert to index
        result_board[index] = block
    
    return ''.join(result_board)

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
