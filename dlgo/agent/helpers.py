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
