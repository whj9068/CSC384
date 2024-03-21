"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


#global variable
min_caching = dict()
max_caching = dict()
alpha_caching = dict()
beta_caching = dict()

# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    score = get_score(board)
    
    if color == 2:
        return (score[1]-score[0])
    else:
        return (score[0]-score[1])


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #evaulate based on the own heuristic and add weight 
    size =  len(board)
    result = compute_utility(board, color)
    if size<=6:
        return result
    result *= 70

    #evaulate based on the corner on the essential position of the board
    opponent_color = get_opponent(color)
    self_corner_weight = 5000
    self_xsqr_weight = 400
    self_csqr_weight = 220
    self_asqr_weight = 70

    oppo_corner_weight = 5000
    oppo_xsqr_weight = 200
    oppo_csqr_weight = 80
    oppo_asqr_weight = 70

   #get the value of each position
    corner_list = [board[0][0],board[size-1][0],board[0][size-1],board[size-1][size-1]]
    xsqr_list = [board[1][1],board[1][size-2],board[size-2][1],board[size-2][size-2]]
    csqr_list = [board[1][0],board[0][1],board[0][size-2],board[size-2][0],board[size-1][1],board[1][size-1],board[size-2][size-1],board[size-1][size-2]]
    asqr_list = [board[2][0],board[size-3][0],board[0][2],board[0][size-3],board[size-1][2],board[size-1][size-3],board[2][size-1],board[size-3][size-1]]
    
    for disk in corner_list:
        if disk == color:
            result+=self_corner_weight
        elif disk==opponent_color:
            result-=oppo_corner_weight


    for disk in xsqr_list:
        if disk == color:
            result+=self_xsqr_weight
        elif disk==opponent_color:
            result-=oppo_xsqr_weight

    for disk in csqr_list:
        if disk == color:
            result+=self_csqr_weight
        elif disk==opponent_color:
            result-=oppo_csqr_weight


    for disk in asqr_list:
        if disk == color:
            result+=self_asqr_weight
        elif disk==opponent_color:
            result-=oppo_asqr_weight

    #add the value of the differnece in the number of moves 
    own_move =len(get_possible_moves(board,color))
    opponent_move = len(get_possible_moves(board,opponent_color))

    result+=(own_move-opponent_move)*70

    #IMPLEMENT
    return result

#helper function for alpha beta pruning    
#function to get the list of after move board
def after_move_board_list(board,color,moves_list,ordering):
    new_board_list = []
    board_move_dict = {}
    for move in moves_list:
        new_board = play_move(board, color, move[0], move[1])
        new_board_list.append(new_board)
        board_move_dict[new_board] = move

    if ordering == 1:
        new_board_list.sort(key = lambda x: compute_heuristic(x, color),reverse=True)

    return new_board_list,board_move_dict

#function to get the opponent of the player
def get_opponent(player):
    if player == 1:
        return 2
    else:
        return 1

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):

    #caching issue
    board_key = tuple(tuple(row) for row in board)

    # Check if the board state is in the cache
    if caching and board_key in min_caching:
        # Return the cached value
        return min_caching[board_key]

    #check if limit is 0
    if limit == 0:
        heu = compute_utility(board, color)
        return (None, heu) 


    best_move = None
    minimum_utility = float('inf')
    opponent_color = get_opponent(color)

    #get the move list for opponent
    possbile_move_list = get_possible_moves(board,opponent_color)
   
   
    #if no possible move return 
    if len(possbile_move_list) == 0:
        heu = compute_utility(board, color)
        return (None, heu)  


    for move in possbile_move_list:

        after_move_board = play_move(board,opponent_color,move[0],move[1])

        current_utility = minimax_max_node(after_move_board,color,limit-1,caching)[1]

        if current_utility<minimum_utility:
            best_move,minimum_utility = move,current_utility
            
    
        #caching the best move and the utility
    if caching == 1:
        min_caching[board_key] = (best_move,minimum_utility)

    return (best_move,minimum_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #caching issue
    board_key = tuple(tuple(row) for row in board)

    # Check if the board state is in the cache
    if caching and board_key in max_caching:
        # Return the cached value
        return max_caching[board_key]
    
    #if limit is 0
    if limit == 0:
        heu = compute_utility(board, color)
        return (None, heu) 


    best_move = (-1,-1)
    maximum_utility = float('-inf')
    opponent_color = get_opponent(color)

    #get the move list
    possbile_move_list = get_possible_moves(board,color)
   
    #if no possible move return 
    if len(possbile_move_list) == 0 :
        heu = compute_utility(board, color)
        return (None, heu)  


    for move in possbile_move_list:

        after_move_board = play_move(board,color,move[0],move[1])

        current_utility = minimax_min_node(after_move_board,color,limit-1,caching)[1]

        if current_utility>maximum_utility:
            best_move,maximum_utility = move,current_utility

    #caching the best move and the utility
    if caching == 1:
        max_caching[board_key] = (best_move,maximum_utility)
            
    return (best_move,maximum_utility)


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
    min_caching.clear()
    max_caching.clear()
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    #caching issue
    board_key = tuple(tuple(row) for row in board)

    # Check if the board state is in the cache
    if caching and board_key in beta_caching:
        # Return the cached value
        return beta_caching[board_key]
    
    #check depth limit 
    if limit == 0:
        heu =  compute_utility(board, color)
        return (None, heu)

    #IMPLEMENT (and replace the line below)
    best_move = (-1,-1)
    minimum_utility = float('inf')
    opponent_color = get_opponent(color)

    #get the move list
    possbile_move_list = get_possible_moves(board,opponent_color)
    
    #check if there is possible move
    if len(possbile_move_list) == 0:
        heu = compute_utility(board, color)
        return (None, heu)    


    board_list,board_move_dict = after_move_board_list(board,opponent_color,possbile_move_list,ordering)

    #loop all the possible move and  recursively call the max node to get the utility
    for after_move_board in board_list:
        move = board_move_dict[after_move_board]
        # after_move_board = play_move(board,opponent_color,move[0],move[1])
        current_utility = alphabeta_max_node(after_move_board,color,alpha,beta,limit-1,caching,ordering)[1]
      
        if current_utility<minimum_utility:
            best_move,minimum_utility = move,current_utility

        beta = min(beta,minimum_utility)

        if beta<=alpha:
            break

    #caching the best move and the utility
    if caching == 1:
        beta_caching[board_key] = (best_move,minimum_utility)

    return best_move,minimum_utility


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    #caching issue
    board_key = tuple(tuple(row) for row in board)

    # Check if the board state is in the cache
    if caching and board_key in alpha_caching:
        # Return the cached value
        return alpha_caching[board_key]

    #check depth limit 
    if limit == 0:
        heu =  compute_utility(board, color)
        return (None, heu)
    
    best_move = (-1,-1)
    maximum_utility = float('-inf')
    opponent_color = get_opponent(color)
   
    #get the move list
    possbile_move_list = get_possible_moves(board,color)

    #check if there is possible move
    if len(possbile_move_list) == 0:
        heu = compute_utility(board, color)
        return (None, heu)    
    

    board_list,board_move_dict = after_move_board_list(board,color,possbile_move_list,ordering)

    #loop all the possible move and  recursively call the max node to get the utility
    for after_move_board in board_list:
        move = board_move_dict[after_move_board]

        current_utility = alphabeta_min_node(after_move_board,color,alpha,beta,limit-1,caching,ordering)[1]
      
        if current_utility>maximum_utility:
            best_move,maximum_utility = move,current_utility

        alpha = max(alpha,maximum_utility)

        if beta<=alpha:
            break

    #caching the best move and the utility
    if caching == 1:
        alpha_caching[board_key] = (best_move,maximum_utility)

    return best_move,maximum_utility


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
    #IMPLEMENT
    alpha_caching.clear()
    beta_caching.clear()
    return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0]

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("test AI") # First line is the name of this AI
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
