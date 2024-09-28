import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

# Helper function to get the index from coordinates
def get_index(row, col, width):
    return row * width + col

# Move the piece in the given direction
def move_piece(board_dict, move, width):
    # Find the empty space coordinates
    empty_space = next((k for k, v in board_dict.items() if v == '@'), None)
    empty_row, empty_col = board_dict[empty_space]
    
    for direction in move:
        if direction == 'N':
            new_row, new_col = empty_row - 1, empty_col
        elif direction == 'S':
            new_row, new_col = empty_row + 1, empty_col
        elif direction == 'E':
            new_row, new_col = empty_row, empty_col + 1
        elif direction == 'W':
            new_row, new_col = empty_row, empty_col - 1
        else:
            continue
        
        # Check if the new position is within bounds and not out of the board
        if 0 <= new_row < 4 and 0 <= new_col < width:
            # Get the letter that will move into the empty space
            for letter, (row, col) in board_dict.items():
                if (row, col) == (new_row, new_col):
                    # Swap positions
                    board_dict[letter], board_dict[empty_space] = (empty_row, empty_col), (new_row, new_col)
                    break
            
            # Update the empty space coordinates
            empty_row, empty_col = new_row, new_col
            
    # Create the resultant board string
    result_board = ['@'] * (width * 4)  # 4 rows for a Klotski board
    for letter, (row, col) in board_dict.items():
        result_board[get_index(row, col, width)] = letter
    return ''.join(result_board)

@app.route('/klotski', methods=['POST'])
def klotski():
    data = request.json
    result_boards = []
    width = 4  # Assuming a fixed width for a Klotski board
    
    for item in data:
        board = item["board"]
        moves = item["moves"]
        
        # Initialize board dictionary
        board_dict = {board[i]: (i // width, i % width) for i in range(len(board))}
        
        result_board = move_piece(board_dict, moves, width)
        result_boards.append(result_board)
    
    return jsonify(result_boards)

if __name__ == '__main__':
    app.run(debug=True)