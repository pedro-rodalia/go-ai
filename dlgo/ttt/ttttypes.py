import enum
from collections import namedtuple


# In tic tac toe two players play against each other, one usin x's and the other
# one using o's
class Player(enum.Enum):
    x = 1
    o = 2

    @property
    def other(self):
        return Player.x if self == Player.o else Player.o


# A point is defined very similarly as how it is defined in Go, but in this case
# a point won't change once it has been initialized
class Point(namedtuple('Point', 'row col')):
    def __deepcopy__(self, memodict={}):
        # These are very immutable.
        return self
