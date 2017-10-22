
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log
import sys
from p3_t3 import Board

num_nodes = 1000
explore_faction = 2.
root_node = MCTSNode(parent=None, parent_action=None)
fun_board = Board()
root_node.untried_actions = fun_board.legal_actions(fun_board.starting_state())
started = False
identity_of_bot = None
visited_boxes = set()



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
        selection_dict = {}
        child_actions = node.child_nodes.keys()
        available_actions = fun_board.legal_actions(state)
        box_x = available_actions[0][1]
        box_y = available_actions[0][0]

        if fun_board.owned_boxes(state)[(box_y, box_x)] != 0:
            global visited_boxes
            visited_boxes.add((box_y, box_x))

            available_actions = fun_board.legal_actions(fun_board.starting_state())

            for action in available_actions:
                if (action[1], action[0]) in visited_boxes:
                    available_actions.remove(action)


        for child_action in child_actions:
            if child_action in available_actions:
                child_node = node.child_nodes[child_action]

                selection = (child_node.wins / child_node.visits) + \
                            (explore_faction * sqrt(log(node.visits)/child_node.visits))
                selection_dict[selection] = (child_node, child_action)

                #node.untried_actions.remove(child_action)

        if len(selection_dict) == 0:
            break

        if fun_board.current_player(state) == identity:
            selection_num = max(selection_dict, key=float)
        else:
            selection_num = min(selection_dict, key=float)

        #try:
        #    node.untried_actions.remove(selection_dict[selection_num][1])
        #except ValueError:
        #    pass

        node = selection_dict[selection_num][0]

    return node
    # hint: return leaf_node


def expand_leaf(node, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

    Returns:    The added child node.

    """
    #action = list(set(fun_board.legal_actions(state)) - set(node.untried_actions))
    #action = choice(fun_board.legal_actions(state))
    #if len(node.untried_actions) == 0:
    #    print
    if len(node.untried_actions) == 0:
        return node
    action = choice(node.untried_actions)
    node.untried_actions.remove(action)

    new_node = MCTSNode(parent=node, parent_action=action, action_list=node.untried_actions)
    node.child_nodes[action] = new_node


    return new_node


def rollout(state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    """
    while not fun_board.is_ended(state):
        possible_moves = fun_board.legal_actions(state)
        next_move = choice(possible_moves)
        state = fun_board.next_state(state, next_move)
    return state


def backpropagate(node, won):
    # If winning node, won = True
    # else won = False
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    tried_action = node.parent_action

    while node is not None:
        if tried_action in node.untried_actions:
            node.untried_actions.remove(tried_action)
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
    if not started:
        global started
        started = True
        global identity_of_bot
        identity_of_bot = board.current_player(state)

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node
        node = traverse_nodes(node, sampled_game, identity_of_bot)

        leaf_node = expand_leaf(node, sampled_game)
        sampled_game = rollout(sampled_game)

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
    print(root_node.child_nodes.keys())
    for action in root_node.child_nodes.keys():
        child_node = root_node.child_nodes[action]
        ratio = child_node.wins / child_node.visits
        if ratio >= best_ratio:
            best_ratio = ratio
            best_action = action

    global root_node
    root_node = node

    if best_action is None:
        print

    return best_action

        # Do MCTS - This is all you!

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    #return None
