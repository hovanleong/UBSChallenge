import json
import logging

from flask import Flask, request, jsonify

from routes import app

logger = logging.getLogger(__name__)

# Function to move the pieces based on the moves string
def move_pieces(board, moves):
    block_positions = list(board)
    directions = {
        'N': (-1, 0),  # Move up
        'S': (1, 0),   # Move down
        'E': (0, 1),   # Move right
        'W': (0, -1)   # Move left
    }

    # Process moves in pairs
    for i in range(0, len(moves), 2):
        block = moves[i]
        direction = moves[i + 1]
        all_curr = [i for i, c in enumerate(block_positions) if c == block]

        if len(all_curr) == 1:
            for j in all_curr:
                block_position = j
                target_position = block_position + directions[direction][0] * 4 + directions[direction][1]
                block_positions.insert(target_position, block)
                temp = block_positions.pop(target_position + 1)
                block_positions.pop(block_position)
                block_positions.insert(block_position, temp)

        if len(all_curr) == 2:
            all_curr_blanks = [i for i, c in enumerate(block_positions) if c == '@']
            if (all_curr[0] == all_curr[1] - 1 and ((all_curr_blanks[0] == all_curr[0] - 4 and all_curr_blanks[1] == all_curr[1] - 4) or (all_curr_blanks[0] == all_curr[0] + 4 and all_curr_blanks[1] == all_curr[1] + 4))) or (all_curr[0] == all_curr[1] - 4 and ((all_curr_blanks[0] == all_curr[0] + 1 and all_curr_blanks[1] == all_curr[1] + 1) or (all_curr_blanks[0] == all_curr[0] - 1 and all_curr_blanks[1] == all_curr[1] - 1))):
                for j in all_curr:
                    block_position = j
                    target_position = block_position + directions[direction][0] * 4 + directions[direction][1]
                    block_positions.insert(target_position, block)
                    temp = block_positions.pop(target_position + 1)
                    block_positions.pop(block_position)
                    block_positions.insert(block_position, temp)
            
            elif all_curr[0] == all_curr[1] - 1:
                if direction == 'W': # shift left
                    block_positions.insert(all_curr[0] - 1, block)
                    block_positions.pop(all_curr[0])
                    block_positions.insert(all_curr[1], '@')
                    block_positions.pop(all_curr[1] + 1)
                else: # shift right
                    block_positions.insert(all_curr[1] + 1, block)
                    block_positions.pop(all_curr[1] + 2)
                    block_positions.insert(all_curr[0], '@')
                    block_positions.pop(all_curr[0] + 1)

            else: 
                if direction == 'N': # shift up
                    block_positions.insert(all_curr[0] - 4, block)
                    block_positions.pop(all_curr[0] - 3)
                    block_positions.insert(all_curr[1], '@')
                    block_positions.pop(all_curr[1] + 1)
                else: # shift down
                    block_positions.insert(all_curr[1] + 4, block)
                    block_positions.pop(all_curr[1] + 5)
                    block_positions.insert(all_curr[0], '@')
                    block_positions.pop(all_curr[0] + 1)

        if len(all_curr) == 4:
            all_curr_blanks = [i for i, c in enumerate(block_positions) if c == '@']
            if all_curr[0] > all_curr_blanks[0]:
                if all_curr[0] == all_curr_blanks[0] + 4: # shift up
                    block_positions.insert(all_curr_blanks[0], block)
                    block_positions.pop(all_curr_blanks[0] + 1)
                    block_positions.insert(all_curr_blanks[1], block)
                    block_positions.pop(all_curr_blanks[1] + 1)
                    block_positions.insert(all_curr[2], '@')
                    block_positions.pop(all_curr[2] + 1)
                    block_positions.insert(all_curr[3], '@')
                    block_positions.pop(all_curr[3] + 1)

                if all_curr[0] == all_curr_blanks[0] + 1: # shift left
                    block_positions.insert(all_curr_blanks[0], block)
                    block_positions.pop(all_curr_blanks[0] + 1)
                    block_positions.insert(all_curr_blanks[1], block)
                    block_positions.pop(all_curr_blanks[1] + 1)
                    block_positions.insert(all_curr[1], '@')
                    block_positions.pop(all_curr[1] + 1)
                    block_positions.insert(all_curr[3], '@')
                    block_positions.pop(all_curr[3] + 1)

            else:
                if all_curr[0] == all_curr_blanks[0] - 8: # shift down
                    block_positions.insert(all_curr_blanks[0], block)
                    block_positions.pop(all_curr_blanks[0] + 1)
                    block_positions.insert(all_curr_blanks[1], block)
                    block_positions.pop(all_curr_blanks[1] + 1)
                    block_positions.insert(all_curr[0], '@')
                    block_positions.pop(all_curr[0] + 1)
                    block_positions.insert(all_curr[1], '@')
                    block_positions.pop(all_curr[1] + 1)

                if all_curr[0] == all_curr_blanks[0] - 2: # shift right
                    block_positions.insert(all_curr_blanks[0], block)
                    block_positions.pop(all_curr_blanks[0] + 1)
                    block_positions.insert(all_curr_blanks[1], block)
                    block_positions.pop(all_curr_blanks[1] + 1)
                    block_positions.insert(all_curr[0], '@')
                    block_positions.pop(all_curr[0] + 1)
                    block_positions.insert(all_curr[2], '@')
                    block_positions.pop(all_curr[2] + 1)

    return ''.join(block_positions)

move_pieces("BCDEBCFGAAFGAAHHI@@J", "IEIEASBSCSDWDWEWEWFNGNHNINIEAE")

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
