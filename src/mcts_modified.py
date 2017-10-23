from _pytest.compat import NoneType

from mcts_node import MCTSNode
from random import choice
from math import sqrt, log
import sys
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

        available_actions = fun_board.legal_actions(node.state)
        #print(available_actions)

        box_x = available_actions[0][1]
        box_y = available_actions[0][0]


        if fun_board.owned_boxes(state)[(box_y, box_x)] != 0:
            global visited_boxes
            visited_boxes.add((box_y, box_x))
            backup_actions = fun_board.legal_actions(fun_board.starting_state())

            for box in visited_boxes:
                for action in backup_actions:
                    if action[0] == box[0] and action[1] == box[1]:
                        backup_actions.remove(action)
            for action in child_actions:
                node.child_nodes[action].untried_actions += backup_actions
            #print(backup_actions)
            #
            # if box_y == box[0] and box_x == box[1]:
            #     for
            #
            # for action in available_actions:
            #     if fun_board.owned_boxes(state)[action[0], action[1]] != 0:
            #         available_actions.remove(action)

        #print(available_actions)


        for child_action in child_actions:
            if child_action in available_actions:
                child_node = node.child_nodes[child_action]

                selection = (child_node.wins / child_node.visits) + \
                            (explore_faction * sqrt(log(node.visits)/child_node.visits))
                selection_dict[selection] = (child_node, child_action)


        if len(selection_dict) == 0:
            return node

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
    try:
        action = node.untried_actions.pop()
    except IndexError:
        return node



    new_node = MCTSNode(parent=node, parent_action=action)
    new_node.state = fun_board.next_state(node.state, action)
    new_node.untried_actions = fun_board.legal_actions(new_node.state)
    #new_node.untried_actions = list(set(node.untried_actions + list(node.child_nodes.keys())) - set(list(action)))
    node.child_nodes[action] = new_node


    # #action = list(set(fun_board.legal_actions(state)) - set(node.untried_actions))
    # #action = choice(fun_board.legal_actions(state))
    # #if len(node.untried_actions) == 0:
    # #    print
    #
    #
    # # print(fun_board.legal_actions(node.state))
    # possible_actions = node.untried_actions
    # # action = choice(fun_board.legal_actions(node.state))
    #
    # action = list(set(possible_actions) & set(fun_board.legal_actions(node.state)))
    # if len(action) == 0:
    #     return node
    #
    # action = choice(action)
    #
    # # while action not in possible_actions:
    # #     action = choice(fun_board.legal_actions(node.state))
    #
    # #possible_actions = []
    # #for action in node.untried_actions:
    # #    if action in fun_board.legal_actions(state):
    # #        possible_actions.append(action)
    #
    # # possible_actions = node.untried_actions
    #
    # #possible_actions = list(set(node.untried_actions) - set(action))
    # possible_actions.remove(action)
    #
    #

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
    #ried_action = node.parent_action
    #node.untried_actions.remove(tried_action)

    while node is not None:
        # if tried_action in node.untried_actions:
            # if node.parent is not None:
            #    node.untried_actions.remove(tried_action)
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
    # if not started:
    #     global started
    #     started = True
    #     global identity_of_bot
    #     identity_of_bot = board.current_player(state)
    #
    #     global root_node
    #     root_node.state = state
    #
    # activity_list = []
    # unpacked = board.unpack_state(state)['pieces']
    # for piece in unpacked:
    #     activity = (piece['outer-row'],piece['outer-column'],piece['inner-row'],piece['inner-column'])
    #     activity_list.append(activity)
    #
    # if len(done_activities) == 0:
    #     if len(activity_list) != 0:
    #         new_activity = activity_list[0]
    #         global done_activities
    #         done_activities.append(new_activity)
    # else:
    #     # try:
    #
    #     new_activity = list(set(activity_list) - set(done_activities))[0]
    #     global done_activities
    #     done_activities.append(new_activity)
    #     next_state = board.next_state(state, new_activity)
    #     if board.is_ended(next_state):
    #         global done_activities
    #         done_activities = []
    #         global root_node
    #         root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    #         new_activity = None
    #         global root_node
    #         root_node.state = state
    #         global visited_boxes
    #         visited_boxes = set()
    #         global done_activities
    #         done_activities = []
    #         print(board.points_values(state))
    #

        # except IndexError:
        #     #reset for next game
        #     global done_activities
        #     done_activities = []
        #     global root_node
        #     root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
        #     new_activity = None
        #     global root_node
        #     root_node.state = state
        #     global visited_boxes
        #     visited_boxes = set()
        #     global done_activities
        #     done_activities = []
        #     print(board.points_values(state))
        #     # global root_node
        #     # root_node.untried_actions = board.legal_actions(state)


    # new_activity = list(set(activity_list) - set(root_node.parent_action))
    #
    # if started:
    #     if new_activity is not None:
    #         node = root_node
    #         global root_node
    #         try:
    #             root_node = root_node.child_nodes[new_activity]
    #         except KeyError:
    #             print
    #
    # if not started:
    #     global started
    #     started = True
    #     global identity_of_bot
    #     identity_of_bot = board.current_player(state)
    #
    #     global root_node
    #     root_node.state = state
    #     global root_node
    #     root_node.untried_actions = board.legal_actions(state)

    identity_of_bot = board.current_player(state)

    for step in range(num_nodes):
        sampled_game = state

        # Start at root
        root_node = MCTSNode(parent=None, parent_action=None)
        node = root_node
        node.untried_actions = fun_board.legal_actions(state)
        node.state = sampled_game
        node = traverse_nodes(node, sampled_game, identity_of_bot)

        leaf_node = expand_leaf(node, sampled_game)
        # sampled_game = rollout(sampled_game)
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

    # global root_node
    # root_node = root_node.child_nodes[best_action]

    if best_action is None:
        print(node)
    print(best_action)
    return best_action

    #done_activities.append(best_action)
    #print(best_action)

    # next_state = board.next_state(state, best_action)
    # if board.is_ended(next_state):
    #     global done_activities
    #     done_activities = []
    #     global root_node
    #     root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    #     new_activity = None
    #     global root_node
    #     root_node.state = state
    #     global visited_boxes
    #     visited_boxes = set()
    #     global done_activities
    #     done_activities = []
    # return best_action

        # Do MCTS - This is all you!

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    #return None
