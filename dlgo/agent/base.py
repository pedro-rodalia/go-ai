# Definition of the interface all our bots will follow
class Agent:

    def __init__(self):
        pass

    # Our bot will select any valid move that doesn't fill one of its own eyes
    def select_move (self, game_state):
        raise NotImplementedError()
