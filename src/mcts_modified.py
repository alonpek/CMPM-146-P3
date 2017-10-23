from _pytest.compat import NoneType

from mcts_node import MCTSNode
from random import choice
from math import sqrt, log
from p3_t3 import Board

num_nodes = 1000
explore_faction = 2.
fun_board = Board()


def traverse_nodes(node, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        state:      The state of the game.
        identity:   The bot'as identity, either '1' or '2'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    # dictionaries evaluates to False if empty
    while node.child_nodes:

        if len(node.untried_actions) != 0:
            return node

        selection_dict = {}
        child_actions = node.child_nodes.keys()



        for child_action in child_actions:

            child_node = node.child_nodes[child_action]

            if fun_board.current_player(node.state) == identity:
                selection = (child_node.wins / child_node.visits) + \
                            (explore_faction * sqrt(log(node.visits)/child_node.visits))
                selection_dict[selection] = (child_node, child_action)
            else:
                selection = (1 - (child_node.wins / child_node.visits)) + \
                            (explore_faction * sqrt(log(node.visits)/child_node.visits))
                selection_dict[selection] = (child_node, child_action)

        selection_num = max(selection_dict, key=float)
        node = selection_dict[selection_num][0]

    return node


def expand_leaf(node, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

    Returns:    The added child node.

    """
    try:
        action = node.untried_actions.pop()
    except IndexError:
        return node



    new_node = MCTSNode(parent=node, parent_action=action)
    new_node.state = fun_board.next_state(node.state, action)
    new_node.untried_actions = fun_board.legal_actions(new_node.state)
    node.child_nodes[action] = new_node


    return new_node

def rollout(state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    """

    while not fun_board.is_ended(state):
        available_actions = fun_board.legal_actions(state)
        box_x = available_actions[0][1]
        box_y = available_actions[0][0]
        next_move = choice(available_actions)
        state = fun_board.next_state(state, next_move)

        for action in available_actions:
            played_state = fun_board.next_state(state, action)
            if fun_board.owned_boxes(played_state)[(box_y, box_x)] == 2:
                if fun_board.current_player(state) == 2:
                    state = fun_board.next_state(state, action)
                    break
            if fun_board.owned_boxes(played_state)[(box_y, box_x)] == 1:
                if fun_board.current_player(state) == 1:
                    state = fun_board.next_state(state, action)
                    break

    return state

def backpropagate(node, won):
    # If winning node, won = True
    # else won = False
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        node = node.parent
    pass



def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)

    # start at root
    root_node = MCTSNode(parent=None, parent_action=None)
    node = root_node
    root_node.untried_actions = fun_board.legal_actions(state)

    for step in range(num_nodes):
        sampled_game = state

        # Start at root
        node = root_node
        node.state = sampled_game
        node = traverse_nodes(node, sampled_game, identity_of_bot)

        leaf_node = expand_leaf(node, sampled_game)
        sampled_game = rollout(leaf_node.state)

        won = board.win_values(sampled_game)
        if won is None:
            won = False
        elif won[identity_of_bot] == 1:
            won = True
        else:
            won = False
        backpropagate(leaf_node, won)

    best_action = None
    best_ratio = 0
    for action in root_node.child_nodes.keys():
        child_node = root_node.child_nodes[action]
        ratio = child_node.wins / child_node.visits
        if ratio >= best_ratio:
            best_ratio = ratio
            best_action = action

    if best_action is None:
        print(node)
    print(best_action)
    return best_action


        # Do MCTS - This is all you!

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
