from dlgo.gotypes import Point

# We will hardcode a rule that prevents the bot from filling in its own eyes,
# under the strictest possible definition. For our purposes, an eye is an empty
# point where all adjacent points are filled with friendly stones. We have to
# create a special case for eyes on the edge of the board. In that case all of
# the diagonally adjacent points must contain friendly stones
def is_point_an_eye(board, point, color):

    # An eye must be an empty point
    if board.get(point) is not None:
        return False

    # All adjacent stones must be friendly
    for neighbour in point.neighbours():
        # Check only neighbours inside the grid
        if board.is_on_grid(neighbour):
            neighbour_color = board.get(neighbour)
            # Compare colors
            if neighbour_color != color:
                return False

    # We must control three out of four corners if the point is in the middle
    # of the board, on the edge we must control all corners
    friendly_corners = 0
    off_board_corners = 0

    # Get corners
    corners = point.diagonals()

    # Count friendly corners and off board corners
    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
        else:
            off_board_corners +=1

    # Check if the point is on the edge
    if off_board_corners > 0:
        # Return True if all corners are friendly
        return off_board_corners + friendly_corners == 4
    # Else return True if friendly corners is greater or equal than 3
    return friendly_corners >= 3


# A position evaluation function captures the sense of whether the agent is
# wining or loosing by calculating certain metrics. We will implement a basic
# position evaluation function so we can implement depth pruning allowing our
# bot to be stronger than the naive bot. This first position evaluation function
# works by adding calculating the difference in the count of stones.
def capture_diff(game_state):
    # Store stones from each player
    black_stones = 0
    white_stones = 0
    # Iterate through the board and count stones for each player
    for r in range(1, game_state.baord.num_rows + 1):
        for c in range(1, game_state.board.num_cols + 1):
            # Create a point for this position
            point = gotypes.Point(r, c)
            # Get the color of said point
            color = game_state.board.get(p)
            # Store the count
            if color == gotypes.Player.black:
                black_stones += 1
            else if color == gotypes.Player.white:
                white_stones += 1
    # Get the difference
    diff = black_stones - white_stones
    # If it's black's move return black_stones - white_stones
    if game_state.next_player == gotypes.Player.black:
        return diff
    # If it's white's move return white_stones - black_stones
    else:
        return -1 * diff
