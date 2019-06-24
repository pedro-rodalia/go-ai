# We can now implement the algorithm creating an MCTS agent: We start by
# creating a new tree. The root node is the currenta gem state. Then we
# repeteadly generate rollouts. In this implementation, we loop for a fixed
# number of rounds for each turn; other implementations may run for a specific
# length of time instead.
# Each round begins by walking down the tree until we find a node where we can
# add a child (any board position that has a legal move that isn't yet in the
# tree). The select_move function hides the work of choosing the best branch to
# explore.
# After we find a suitable node, we call add_random_child to pick any follow up
# move and bring it into the tree. At this point, node is a newly created MCTS
# Node that has zero rollouts.
# We now start a rollout from this node by calling simulate_random_game. The
# implementation of simulate_random_game is identical to the bot_v_bot example.
# Finally we update the win counts of the newly created node and all its
# ancestors.
class MCTSAgent(agent.Agent):

    # We define the function that selects a child based on its UTC score
    # calculated using the helper function at the end of this file
    def select_child(self, node):
        # Get total number of rollouts from the node's children
        total_rollouts = sum(child.num_rollouts for child in node.children)
        # Start best score at -1
        best_score = -1
        # And best child as None
        best_child = None
        # Iterate trough the children and look for the best UCT score
        for child in node.children:
            # Calculate the score
            score = uct_score(
                total_rollouts,
                child.num_rollouts,
                child.winning_frac(node.game_state.next_player),
                self.temperature)
            # If the score is better than the best score recorded
            if score > best_score:
                # Update score
                best_score = score
                # And store the child
                best_child = child
        # Return the chosen child
        return best_child

    # Function that returns the selected node
    def select_move(self, game_state):
        # Initialize the tree creating a root node from current game_state
        root = MCTSNode(game_state)
        # Loop for a number of rounds (this can be changed to time)
        for i in range(self.num_rounds):
            # The starting node will be the root
            node = root
            # Look for the deepest child that is not a leaf
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)
            # If the node can have children, add a new child to the tree
            if node.can_add_child():
                node = node.add_random_child()
            # Simulate a random game from this node
            winner = self.simulate_random_game(node.game_state)
            # Propagate the score upt the tree
            while node is not None:
                node.record_win(winner)
                node = node.parent
        # After we are done looping, we have to select the best move by looking
        # at the scores
        best_move = None
        best_percentage = -1.0
        # Loop through the children looking for the best move
        for child in root.children:
            # Get percentage of wins over loses
            child_percentage = child.winning_frac(game_state.next_player)
            # If the score is better than the last best score recorded
            if child_percentage > best_percentage:
                # Update the last best score
                best_percentage = child_percentage
                # Store the move
                best_move = child_move
        # Return the selected move
        return best_move


# We have to select a branch to explore using the BCT formula so we have to use
# a function like this one (which implements the UCT formulae):
def uct_score(parent_rollouts, children_rollouts, win_percentage, temperature):
    exploration = math.sqrt(math.log(parent_rollouts) / children_rollouts)
    return win_percentage + temperature * exploration
