from dlgo.gotypes import Player
import copy

# We need a structure to represent the actions a player can take on a turn
# Normally, a turn involves placing a stone on the board, but a player can
# also pass or resign at any time. Following American Go Association (AGA)
# conventions, we use the term move to mean any of those three actions, wheras
# a play refers to placing a stone. In the move class we therefore encode all
# three types of move (play, pass, resign) and make sure a move has precisely
# one of these types. For actual plays we need to pass a Point to be placed.

# A Move is any action a player can play on a turn.
class Move():

    # Clients generally won't call the Move constructor directly. Instead,
    # we usually call Move.play, Move.resign or Move.pass to construct an
    # instance of a Move.
    def __init__(self, point = None, is_pass = False, is_resign = False):
        # Make sure the move has one of the three types
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        # If point is set, the move is play
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    # This move places a stone on the board
    @classmethod
    def play(cls, point):
        return Move(point = point)

    # This move passes
    @classmethod
    def pass(cls):
        return Move(is_pass = True)

    # This move resigns the current game
    @classmethod
    def resign(cls):
        return Move(is_resign = True)
