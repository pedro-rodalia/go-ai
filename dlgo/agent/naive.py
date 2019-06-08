from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point
import random

# Our first implementation will be as naive as posible: It'll randomly
# select any valid move that doesn't fill in one of its own ayes. If no such
# move exists, it'll pass. This bot will play at the 30kyu level, an absolute
# begginner
class RandomBot(Agent):

    def select_move(self, game_state):
        """Choose a random valid  move that preserves our own eyes"""
        # Get points that are a candidate for placing a stone
        candidates = []
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                candidate = Point(row = r, col = c)
                # If a point within the board is a valid move, save it as a
                # candidate
                if game_state.is_valid_move(Move.play(candidate)) and \
                    not is_point_an_eye(game_state.board,
                                        candidate,
                                        game_state.next_player):
                    candidates.append(candidate)
        # If there are no candidates, pass
        if not candidates:
            return Move.pass_turn()
        # Else choose randomly among all the candidate
        return Move.play(random.choice(candidates))
