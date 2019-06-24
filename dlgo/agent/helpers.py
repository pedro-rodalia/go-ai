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

# This functions implements depth prunning similarly to how the minimax code
# does. Here instead of returning a win/lose/draw enum, we return a number
# indicating the value of our board evaluation function. Our convention is that
# the score is from the perspective of the player who has the next turn: a large
# score means the player who has the next move expects to win. When we evaluate
# the board from our opponent's perspective, we multiply the score by -1 to flip
# back to our perspective.
# The max_depth parameter controls the number of moves we want to search ahead.
# At each turn, we subtract 1 from this value.
# When max_depth hits 0, we stop searching and call our board evaluation
# function.
def best_result(game_state, max_depth, eval_fn):
    # If the game is already over we already know who the winner is
    if game_state.is_over():
        if game_state.winner() == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE
    # If we have reached the maximum depth, we run our evaluation function
    if max_depth == 0:
        # Assigned to op_best_outcome when recursivity ends for each loop
        return eval_fn(game_state)
    # Best result starts as the worse case
    best_so_far = MIN_SCORE
    # Loop over all possible moves
    for candidate_move in game_state.legal_moves():
        # Make the move and see what the board would look like
        next_state = game_state.apply_move(candidate_move)
        # Recursively run this fn to see the best result for the oponent
        opponent_best_outcome = best_result(next_state, max_depth - 1, eval_fn)
        # Our outcome would be the opposite
        our_outcome = -1 * opponent_best_outcome
        # If our result is better than any other result evaluated to this moment
        if our_outcome > best_so_far:
            # Save it
            best_so_far = our_outcome
    # Return best result so far after having evaluated all situations
    return best_so_far


# With alpha-beta prunning we can discard branches by checking the result each
# time we reach the end of our depth search. If the result is worse for us than
# the best result we have found, we can stop checking posibilities for that
# branch, because it can lead us to a worse result than the one we have stored.
# best_black = beta; best_white = alpha
def alpha_beta_result(game_state, max_depth, alpha, beta, eval_fn):
    # If the game is already over we already know who the winner is
    if game_state.is_over():
        if game_state.winner() == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE
    # If we have reached the maximum depth, we run our evaluation function
    if max_depth == 0:
        # Assigned to op_best_outcome when recursivity ends for each loop
        return eval_fn(game_state)
    # Best result starts as the worse case
    best_so_far = MIN_SCORE
    # Loop over all possible moves
    for candidate_move in game_state.legal_moves():
        # Make the move and see what the board would look like
        next_state = game_state.apply_move(candidate_move)
        # Recursively run this fn to see the best result for the oponent
        opponent_best_outcome = alpha_beta_result(
            next_state, max_depth - 1, alpha, beta, eval_fn)
        # Our outcome would be the opposite
        our_outcome = -1 * opponent_best_outcome
        # If our outcome is the best we've seen so far
        if our_outcome > best_so_far:
            # store it as best_so_far
            best_so_far = our_result
        # Chosing a move for White's
        if game_state.next_player == Player.white:
            # and the best result so far for him is better than the previous
            if best_so_far > alpha
                # Update the benchmark for White
                alpha = best_so_far
            # Outcome for black would be the opposite
            outcome_for_black = -1 * best_so_far
            # We are picking a move for white, so it only needs to be strong
            # enough to eliminate black's previous move.
            if outcome_for_black < beta
                # Return best result so far
                return best_so_far
        # Chosing a move for Black's
    elif game_state.next_player == Player.black:
            # and the best result so far for him is better than the previous
            if best_so_far > beta
                # Update the benchmark for Black
                beta = best_so_far
            # Outcome for white would be the opposite
            outcome_for_white = -1 * best_so_far
            # We are picking a move for black, so it only needs to be strong
            # enough to eliminate white's previous move.
            if outcome_for_white < alpha
                # Return best result so far
                return best_so_far
    # Return best result so far after having evaluated the necessary situations
    return best_so_far
