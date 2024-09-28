import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

# Directions mapping for movements
DIRECTIONS = {
    'N': (-1, 0),  # Move up
    'S': (1, 0),   # Move down
    'E': (0, 1),   # Move right
    'W': (0, -1)   # Move left
}

def parse_board(board_str):
    """Convert board string to a 2D list."""
    return [list(board_str[i:i+4]) for i in range(0, len(board_str), 4)]

def board_to_string(board):
    """Convert a 2D list back to a board string."""
    return ''.join(''.join(row) for row in board)

def find_block(board, block):
    """Find the coordinates of the block on the board."""
    for r in range(5):
        for c in range(4):
            if board[r][c] == block:
                return r, c
    return None

def get_block_shape(board, block):
    """Get the coordinates of all parts of the block."""
    shape = []
    for r in range(5):
        for c in range(4):
            if board[r][c] == block:
                shape.append((r, c))
    return shape

def can_move(board, shape, direction):
    """Check if the block can be moved in the specified direction."""
    dr, dc = direction
    for r, c in shape:
        new_r, new_c = r + dr, c + dc
        if new_r < 0 or new_r >= 5 or new_c < 0 or new_c >= 4 or board[new_r][new_c] != '@':
            return False
    return True

def move_block(board, shape, direction):
    """Move the block on the board."""
    dr, dc = direction
    new_shape = [(r + dr, c + dc) for r, c in shape]

    # Clear the old positions
    for r, c in shape:
        board[r][c] = '@'

    # Set the new positions
    for r, c in new_shape:
        board[r][c] = shape[0]  # Use the block's identifier

def apply_moves(board, moves):
    """Apply the moves to the board."""
    for i in range(0, len(moves), 2):
        block = moves[i]
        direction = moves[i + 1]

        shape = get_block_shape(board, block)
        if shape:  # Ensure the block exists
            if can_move(board, shape, DIRECTIONS[direction]):
                move_block(board, shape, DIRECTIONS[direction])

def process_board(board_str, moves):
    """Process the board and apply the moves."""
    board = parse_board(board_str)
    apply_moves(board, moves)
    return board_to_string(board)

@app.route('/klotski', methods=['POST'])
def klotski():
    """Handle POST requests to /klotski endpoint."""
    data = request.get_json()
    
    results = []
    for item in data:
        board = item['board']
        moves = item['moves']
        result_board = process_board(board, moves)
        results.append(result_board)
    
    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug=True)