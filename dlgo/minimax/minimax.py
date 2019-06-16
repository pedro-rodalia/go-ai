from dlgo.agent.base import Agent as agent
import enum
import random


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#------------------------------    THEORY   ------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


# 4.1 A function that finds a move that immediatly wins the game.
def find_winning_move(game_state, next_player):
    # Iterates over all legal moves that are currently possible
    for candidate_move in gam_state.legal_moves(next_player):
        # Gets the state the game would get into if the move is applied
        next_state = game_state.apply_move(candidate_move)
        # Check if this move would result in the player winning
        if next_state.is_over() and next_state.winner == next_player:
            # This is a winning move, no need to continue searching
            return candidate_move
            # We can't win in this turn as none of the moves made the player win
            return None


# 4.2 A function that avoids giving the opponent a winning move
def eliminate_losing_moves(game_state, next_player):
    # Get opponent player
    opponent = next_player.other()
    # Here we will store all posible moves that can be applied without making
    # the oponent win
    possible_moves = []
    # Iterates over all legal moves that are currently possible
    for candidate_move in game_state.legal_moves(next_player):
        # Gets the state the game would get into if the move is applied
        next_state = game_state.apply_move(candidate_move)
        # Use previos function to determine if applying this move would give
        # the oponent the option to win in it's next move
        opponent_winning_move = find_winning_move(next_state, opponent)
        # If the move doesn't give the opponent the chance to win, store it
        if opponent_winning_move is None:
            possible_moves.append(candidate_move)
            # Return the list of possible moves
            return possible_moves


# 4.3 A function that finds a two move sequence that guarantees a win
def find_two_step_win(game_state, next_player):
    # Get opponent player
    opponent = next_player.other()
    # Iterates over all legal moves that are currently possible
    for candidate_move in game_state.legal_moves(next_player):
        # Gets the state the game would get into if the move is applied
        next_state = game_state.apply_move(candidate_move)
        # Check if the oponent can has losing moves
        good_responses = eliminate_losing_moves(next_state, opponent)
        # if no_losing_moves is empty, it means this move can make us win in two
        # moves
        if not good_responses:
            # No need to keep searching as this move would make us win
            return candidate_move
            # If no move would make us win in two turns, return none
            return None


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#---------------------------    TIC-TAC-TOE   ----------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


# 4.4 An enum to represent the outcome of a game
class GameResult(enum.Enum):
    loss = 1
    draw = 2
    win = 3


# Get the opposite result for a given result
def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    if game_result == GameResult.win:
        return game_result.loss
    return GameResult.draw


# Now the question is how to implement best_result. If the game is already
# over, there's only one possible result. But if we are somewhere in the middle
# we need to search ahead.
def best_result(game_state):
    if game_state.is_over():
        if game_state.winner() == game_state.next_player:
            return GameResult.win
        elif game_state.winner() is None:
            return GameResult.draw
        else:
            return GameResult.loss
    # Start asuming our best move turns into a loss
    best_result_so_far = GameResult.loss
    # Iterate trough candidate moves
    for candidate_move in game_state.legal_moves():
        # See what the board would look like
        next_state = game_state.apply_move(candidate_move)
        # Do the same for the opponent move from next_state
        opponent_best_outcome = best_result(next_state)
        # Our outcome would be the opposite of our opponent's outcome
        our_outcome = reverse_game_result(opponent_best_outcome)
        # Check if this result is better than any of the results checked
        if our_outcome.value > best_result_so_far.value:
            best_result_so_far = our_outcome
    # Return what our best result would be
    return best_result_so_far


# 4.5 A game-playing agent that implements minimax search
class MinimaxAgent(agent):
    # Function that selects the move with the best outcome
    def select_move(self, game_state):
        # Store moves that lead to the three possible results
        winning_moves = []
        draw_moves = []
        losing_moves = []
        for candidate_move in game_state.legal_moves():
            # Get the new game state if this move gets applied
            next_state = game_state.apply_move(candidate_move)
            # Based on the new state, get the opponent best outcome
            opponent_best_outcome = best_result(next_state)
            # Our best outcome is the reverse of the opponent best outcome
            # His win is our loss and viceversa, and draw goes fot the two of us
            our_best_outcome = reverse_game_result(opponent_best_outcome)
            # Compare results from different moves and store the move
            if our_best_outcome == GameResult.win:
                winning_moves.append(candidate_move)
            elif our_best_outcome == GameResult.draw:
                draw_moves.append(candidate_move)
            else:
                losing_moves.append(candidate_move)
        # If we have winning moves choose randomly amongst them
        if winning_moves:
            return random.choice(winning_moves)
        # If we don't have winning moves but we can draw, choose randomly
        # amongst them
        if draw_moves:
            return random.choice(draw_moves)
        # Else we have to choose a losing move because we have no other option
        return random.choice(losing_moves)
