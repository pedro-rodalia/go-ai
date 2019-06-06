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


# We'll keep track of groups of connected stones of the same color and their
# liberties at the same time. Doing so is much more efficient when implementing
# game logic. We call a group of connected stones of the same color a string.
# We can build this structure efficiently with the Python set type.

# Go strings are a chain of connected stones of the same color.
class GoString():

    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    # Removes a liberty from the string
    def remove_liberty(self, point):
        self.liberties.remove(point)

    # Adds a liberty to the string
    def add_liberty(self, point):
        self.liberties.add(point)

    # Returns a new Go string containing all stones in both strings
    def merged_with(self, go_string):
        # Check tha both strings belong to the same player
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)

    # Counts the number of liberties within the go string
    @property
    def num_liberties(self):
        return len(self.liberties)

    # Checks if two go strings are the same by comparing colors, stones and
    # liberties
    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties
