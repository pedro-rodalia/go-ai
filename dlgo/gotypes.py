# coding=UTF-8
from collections import namedtuple
import enum

# Black abd white players take turns in Go, and we use enum to represent the
# different colored stones. A Player is either black or white
class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white

# A named tuple lets us access the coordinates as point.row and point.col
# instead of point[0] and point[1], which makes for much better readability
class Point(namedtuple('Point', 'row col')):

    # Returns neighbours
    def neighbours(self):
        doc = "Returns the four neighbours of a Point instance"
        return [
            Point(self.row - 1, self.col), # Top
            Point(self.row + 1, self.col), # Bottom
            Point(self.row, self.col - 1), # Left
            Point(self.row, self.col + 1), # Right
        ]

    # Returns diagonals
    def diagonals(self):
        doc = "Returns the four diagonals of a Point instance"
        return [
            Point(self.row - 1, self.col - 1 ), # Top
            Point(self.row + 1, self.col - 1 ), # Bottom
            Point(self.row - 1, self.col + 1), # Left
            Point(self.row + 1, self.col + 1), # Right
        ]
