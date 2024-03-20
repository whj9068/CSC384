"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cache = {}

def board_to_key(board):
    # Flatten the board into a single tuple since tuples are hashable and can be used as dictionary keys
    return tuple(item for row in board for item in row)

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    #number of hectares they own minus the number of hectares their competitor owns
    p1_count, p2_count = get_score(board)
    if color == 1:
        return p1_count - p2_count
    else:
        return p2_count - p1_count
    
# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

def count_corner_captures(board, color):
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    
    # Dynamically determine corner positions based on board size
    corners = [(0, 0), (0, cols-1), (rows-1, 0), (rows-1, cols-1)]    
    captures = sum(1 for x, y in corners if board[x][y] == color)
    return captures

def count_mobility(board, color):
    # Assuming get_possible_moves is a function that returns all legal moves for the given color
    return len(get_possible_moves(board, color))

def evaluate_move(board, move, color):
    # Apply the move to a copy of the board
    new_board = play_move(board, color, move[0], move[1])
    
    # Calculate the difference in corner captures as a result of this move
    corner_captures = count_corner_captures(new_board, color) - count_corner_captures(board, color)
    
    # Calculate the change in mobility as a result of this move
    mobility = count_mobility(new_board, color) - count_mobility(board, color)
    
    # Weight these factors (these weights can be adjusted based on strategy)
    score = 10 * corner_captures + mobility
    
    return score


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    global cache
    if caching and board_to_key(board) in cache:
        return cache[board_to_key(board)]
    #IMPLEMENT (and replace the line below)
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    # Get possible moves for the current player, not the opponent.
    moves = get_possible_moves(board, opp_color)
    if len(moves) == 0 or limit == 0:
        # No further moves to evaluate or depth limit reached, compute utility for the current state.
        best_move = None
        min_utility = compute_utility(board, color)
        return (best_move, min_utility)
    else:
        best_move = None
        min_utility = float('inf')
        for move in moves:
            # Play the move for the current player and evaluate.
            new_board = play_move(board, opp_color, move[0], move[1])
            # Recursive call to evaluate the move, using the opponent's color for the next level.
            new_move = minimax_max_node(new_board, color, limit-1, caching)
            # If the utility from this move is less than the current minimum, update the minimum.
            if new_move[1] < min_utility:
                min_utility = new_move[1]
                best_move = move
        if caching:
            cache[board_to_key(board)] = (best_move, min_utility)
        return (best_move, min_utility)


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    global cache
    if caching and board_to_key(board) in cache:
        return cache[board_to_key(board)]
    
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    # Get possible moves for the current player, not the opponent.
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        # No further moves to evaluate or depth limit reached, compute utility for the current state.
        best_move = None
        max_utility = compute_utility(board, color)
        return (best_move, max_utility)
    else:
        best_move = None
        max_utility = float('-inf')
        for move in moves:
            # Play the move for the current player and evaluate.
            new_board = play_move(board, color, move[0], move[1])
            # Recursive call to evaluate the move, using the opponent's color for the next level.
            new_move = minimax_min_node(new_board, opp_color, limit-1, caching)
            # If the utility from this move is greater than the current maximum, update the maximum.
            if new_move[1] > max_utility:
                max_utility = new_move[1]
                best_move = move
        if caching:
            cache[board_to_key(board)] = (best_move, max_utility)
        return (best_move, max_utility)


def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    #IMPLEMENT (and replace the line below)
    move, utility = minimax_max_node(board, color, limit, caching)
    return move #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    global cache
    if caching and board_to_key(board) in cache:
        return cache[board_to_key(board)]
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1
    
    moves = get_possible_moves(board, opp_color)
    
    if ordering:
        moves = sorted(moves, key=lambda move: evaluate_move(board, move, opp_color), reverse=False)

    if len(moves) == 0 or limit == 0:
        best_move = None
        min_utility = compute_utility(board, color)
    else:
        best_move = None
        min_utility = float('inf')
        for move in moves:
            new_board = play_move(board, opp_color, move[0], move[1])
            new_move = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching)
            if new_move[1] < min_utility:
                min_utility = new_move[1]
                best_move = move
            if min_utility <= alpha:
                return (best_move, min_utility)
            beta = min(beta, min_utility)
            if alpha >= beta:
                break
        if caching:
            cache[board_to_key(board)] = (best_move, min_utility)
    return (best_move, min_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    global cache
    if caching and board_to_key(board) in cache:
        return cache[board_to_key(board)]
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    # Generate and evaluate moves for the current player (color)
    moves = get_possible_moves(board, color)
    
    if ordering:
        moves = sorted(moves, key=lambda move: evaluate_move(board, move, color), reverse=True)

    
    if len(moves) == 0 or limit == 0:
        best_move = None
        max_utility = compute_utility(board, color)
        return (best_move, max_utility)
    else:
        best_move = None
        max_utility = float('-inf')
        for move in moves:
            # Play the move for the current player and evaluate
            new_board = play_move(board, color, move[0], move[1])
            # Recursive call to evaluate the move, aiming to minimize the opponent's utility
            new_move = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching)
            if new_move[1] > max_utility:
                max_utility = new_move[1]
                best_move = move
            alpha = max(alpha, max_utility)
            if alpha >= beta:
                break
        if caching:
            cache[board_to_key(board)] = (best_move, max_utility)
    return (best_move, max_utility)

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    #IMPLEMENT (and replace the line below)
    move, utility = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
    return move #change this!

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
