from dlgo import gotypes

# Cols characters stand for the columns of the go board
COLS = 'ABCDEFGHJKLMNOPQRST'
# To display the board on the command line, we encode an empty field with a
# point (·), a black stone with an X and a white stone with an O.
STONE_TO_CHAR = {
    None: ' · ',
    gotypes.Player.black: ' X ',
    gotypes.Player.white: ' O '.
}

# Print function that prints out the next move to the command line
def print_move(player, move):
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resings'
    else:
        move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)
    print('%s %s' % (player, move_str))

# Print function that prints out the board
def print_board(board):
    for row in range(board.num_rows, 0, -1):
        # For aligning cols with numbers with one and two digits
        bump = ' ' if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            # Get the stone for the specific point
            stone = board.get(gotypes.Point(row = row, col = col))
            # Add up stones in the line
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.num_cols]))
