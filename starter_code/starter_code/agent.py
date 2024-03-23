"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

#define the dict for cache for the minimax and alpha-beta
min_cache = {}
max_cache = {}
alpha_max_cache = {}
alpha_min_cache = {}

def board_to_key(board):
    #change the board into a type that can be used as dictionary keys
    return str(board)


def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    #number own minus number of opponent
    p1_count, p2_count = get_score(board)

    if color == 1:
        return p1_count - p2_count
    else:
        return p2_count - p1_count

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    # Determine the board size
    board_size = len(board)

    #get the static weights for this board size
    weights = get_square_weights(board_size)
    
    #calculate current mobility for self
    current_mobility = count_mobility(board, color)
    
    #calculate the sum of square weights for the current board state
    weight_sum = get_square_weight_sum(board, color, weights)
    
    #calculate opponent mobility
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1
    opponent_mobility = count_mobility(board, opp_color)
    
    #add weights to mobility
    #adjust weight for each component based on test trials
    score = (current_mobility-opponent_mobility)*40 + (weight_sum*60)
    
    return score

def get_square_weights(board_size):
    #refered from https://reversiworld.wordpress.com/category/weighted-square-value/
    #with some modifications
    if board_size == 8:
        return [
            120, -20, 20, 5, 5, 20, -20, 120,
            -20, -40, -5, -5, -5, -5, -40, -20,
            20, -5, 15, 3, 3, 15, -5, 20,
            5, -5, 3, 3, 3, 3, -5, 5,
            5, -5, 3, 3, 3, 3, -5, 5,
            20, -5, 15, 3, 3, 15, -5, 20,
            -20, -40, -5, -5, -5, -5, -40, -20,
            120, -20, 20, 5, 5, 20, -20, 120
        ]
    
    elif board_size == 7:
        return [
            120, -30, 20, 20, 20, -30, 120,
            -30, -50, -10, -10, -10, -50, -30,
            20, -10, 5, 0, 5, -10, 20,
            20, -10, 0, 10, 0, -10, 20,
            20, -10, 5, 0, 5, -10, 20,
            -30, -50, -10, -10, -10, -50, -30,
            120, -30, 20, 20, 20, -30, 120,
        ]
    
    elif board_size == 6:
        return [
            120, -30, 20, 20, -30, 120,
            -30, -50, -10, -10, -50, -30,
            20, -10, 5, 5, -10, 20,
            20, -10, 5, 5, -10, 20,
            -30, -50, -10, -10, -50, -30,
            120, -30, 20, 20, -30, 120
        ]
    
    elif board_size == 5:
        return [
            100, -20, 10, -20, 100,
            -20, -40, -5, -40, -20,
            10, -5, 0, -5, 10,
            -20, -40, -5, -40, -20,
            100, -20, 10, -20, 100
        ]
    
    elif board_size == 4:
        return [
            100, -10, -10, 100,
            -10, -20, -20, -10,
            -10, -20, -20, -10,
            100, -10, -10, 100
        ]

def count_mobility(board, color):
    #returns number of all legal moves for the given color
    return len(get_possible_moves(board, color))

def get_square_weight_sum(board, color, weights):
    #calculate the sum of weights for the squares
    #weight = all self weight - all opponent weight
    weight_sum = 0
    for i in range(len(board)):
        for j in range(len(board[i])):
            #self weight
            if board[i][j] == color: 
                weight_sum += weights[i * len(board) + j]
            #opponent weight
            elif board[i][j] == 3 - color:
                weight_sum -= weights[i * len(board) + j]
    return weight_sum


def evaluate_move_max(board, moves, color):
    # List to hold tuples of (utility, new board, move)
    move_evaluations = []

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        # Get utility value of new board and save
        utility = compute_heuristic(new_board, color)
        move_evaluations.append((utility, new_board, move))
    
    # Sort utility in descending order
    move_evaluations.sort(key=lambda x: x[0], reverse=True)
    return move_evaluations

def evaluate_move_min(board, moves, color):
    # List to hold tuples of (utility, new board, move)
    move_evaluations = []

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        # Get utility value of new board and save
        utility = compute_heuristic(new_board, color)
        move_evaluations.append((utility, new_board, move))
    
    # Sort utility in ascending order
    move_evaluations.sort(key=lambda x: x[0], reverse=False)
    return move_evaluations


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    #transform board to type that can be stored as key in dict
    key = board_to_key(board)
    
    #check if this state is in cache already
    #if so, return
    if caching and key in min_cache:
        return min_cache[key]
    
    #get opponent color
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    #get possible moves for the current player
    moves = get_possible_moves(board, opp_color)
    if limit == 0:
        #depth limit reached, compute utility and return
        best_move = None
        min_utility = compute_utility(board, color)
        return (best_move, min_utility)
    
    if len(moves) == 0:
        #no further moves, compute utility and return
        best_move = None
        min_utility = compute_utility(board, color)
        return (best_move, min_utility)
    else:
        #there is further moves to evaluate
        best_move = None
        min_utility = float('inf')

        #traverse through every avaliable moves
        for move in moves:
            #play the move
            new_board = play_move(board, opp_color, move[0], move[1])
            #recursive call to the move
            _ , utility = minimax_max_node(new_board, color, limit-1, caching)
            #if the utility from this move is less than the current minimum
            #update the minimum.
            if utility < min_utility:
                min_utility = utility
                best_move = move
        #save into cache
        if caching:
            min_cache[key] = (best_move, min_utility)
        return (best_move, min_utility)


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    #transform board to type that can be stored as key in dict
    key = board_to_key(board)
    
    #check if this state is in cache already
    #if so, return
    if caching and key in max_cache:
        return max_cache[key]

    #get possible moves for the current player
    moves = get_possible_moves(board, color)
    if limit == 0:
        #no further move, compute utility and return
        best_move = None
        max_utility = compute_utility(board, color)
        return (best_move, max_utility)
    
    if len(moves) == 0:
        #depth limit reached, compute utility and return
        best_move = None
        max_utility = compute_utility(board, color)
        return (best_move, max_utility)
    else:
        best_move = None
        max_utility = float('-inf')

        #traverse through every avaliable moves
        for move in moves:
            #play the move
            new_board = play_move(board, color, move[0], move[1])
            #recursive call to evaluate the move
            _, utility = minimax_min_node(new_board, color, limit-1, caching)
            #if the utility from this move is greater than the current minimum
            #update the minimum
            if utility > max_utility:
                max_utility = utility
                best_move = move
        #save into cache
        if caching:
            max_cache[key] = (best_move, max_utility)
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
    min_cache.clear()
    max_cache.clear()
    move, _ = minimax_max_node(board, color, limit, caching)
    return move #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    #transform board to type that can be stored as key in dict
    key = board_to_key(board)
    
    #check if this state is in cache already
    #if so, return
    if caching and key in alpha_min_cache:
        return alpha_min_cache[key]
    
    #get opponent color
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1
    
    if limit == 0:
        #depth limit reached, compute utility and return
        best_move = None
        min_utility = compute_utility(board, color)
        return (best_move, min_utility)
    
    #get possible moves
    moves = get_possible_moves(board, opp_color)

    if len(moves) == 0:
        #no further moves, compute utility and return.
        best_move = None
        min_utility = compute_utility(board, color)
        return (best_move, min_utility)
    else:
        #with ordering
        if ordering:
            evaluate_moves = evaluate_move_min(board, moves, opp_color)
            best_move = None
            min_utility = float('inf')

            for e in evaluate_moves:
                #traverse boards by utility ranking
                move = e[2]
                #recursive call to evaluate the move
                _, utility = alphabeta_max_node(e[1],color,alpha,beta,limit-1,caching,ordering)
                #if the utility is less than the current minimum
                #update the minimum.
                if utility < min_utility:
                    min_utility = utility
                    best_move = move
                #update beta
                beta = min(beta, min_utility)
                #pruning
                if alpha >= beta:
                    break
        else:
            #without ordering
            best_move = None
            min_utility = float('inf')

            #traverse through every avaliable moves
            for move in moves:
                #play the move
                new_board = play_move(board, opp_color, move[0], move[1])
                #recursive call to evaluate the move
                _, utility = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)
                #if the utility is less than the minimum
                #update the minimum.
                if utility < min_utility:
                    min_utility = utility
                    best_move = move
                #update beta
                beta = min(beta, min_utility)
                #pruning
                if alpha >= beta:
                    break
                
        #save into cache
        if caching:
            alpha_min_cache[key] = (best_move, min_utility)
    return (best_move, min_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    key = board_to_key(board)
    
    # Check if this state is in cache
    #if so, return
    if caching and key in alpha_max_cache:
        return alpha_max_cache[key]
    
    # Get opponent color
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    # If depth limit reached, compute utility and return
    if limit == 0:
        best_move = None
        max_utility = compute_utility(board, color)
        return (best_move, max_utility)
    
    # Get possible moves
    moves = get_possible_moves(board, color)

    # If no moves, compute utility and return
    if len(moves) == 0:
        best_move = None
        max_utility = compute_utility(board, color)
        return (best_move, max_utility)
    else:
        # With ordering
        if ordering:
            evaluate_moves = evaluate_move_max(board, moves, color)
            best_move = None
            max_utility = float('-inf')
            # Traverse boards by utility ranking
            for e in evaluate_moves:
                move = e[2]
                # Recursive call to evaluate the move
                _, utility = alphabeta_min_node(e[1], color, alpha, beta, limit-1, caching, ordering)
                # If the utility is greater than the maximum
                #update the maximum
                if utility > max_utility:
                    max_utility = utility
                    best_move = move
                # Pruning
                alpha = max(alpha, max_utility)
                # Update beta
                if alpha >= beta:
                    break
        else:
            # Without ordering
            best_move = None
            max_utility = float('-inf')
            # Traverse through every available moves
            for move in moves:
                # Play the move
                new_board = play_move(board, color, move[0], move[1])
                # Recursive call to evaluate the move
                _, utility = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)
                # If the utility is greater than the maximum
                # update the maximum
                if utility > max_utility:
                    max_utility = utility
                    best_move = move
                # Pruning
                alpha = max(alpha, max_utility)
                # Update beta
                if alpha >= beta:
                    break

        # Save into cache
        if caching:
            alpha_max_cache[key] = (best_move, max_utility)
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
    alpha_max_cache.clear()
    alpha_min_cache.clear()
    move, _ = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
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
