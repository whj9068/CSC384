"""
An AI player for Othello. 
"""

import random
import sys
import time
import math

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cach = dict()


def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    a, b = get_score(board)
    return a - b if color == 1 else b - a



# Better heuristic value of board
def parity_heuristic(board, color):
    """
    Calculate the parity heuristic for a board state and player color.
    This heuristic evaluates the difference in score between two players,
    normalized by their total score, scaled to 100.
    """
    a, b = get_score(board)
    c = a - b if color == 1 else b - a
    return 100 * c / (a + b)


def mobility_heuristic(board, color):
    """
    Calculates the mobility heuristic for a given board and player color.
    This heuristic evaluates the player's mobility (the number of possible moves)
    relative to their opponent's, normalized and scaled to 100.
    """
    c2 = 3 - color
    move1 = len(get_possible_moves(board, color))
    move2 = len(get_possible_moves(board, c2))
    s_move = move1 + move2
    return 100 * (move1 - move2) / s_move if s_move > 0 else 0


def corner_occupancy_heuristic(board, color):
    """
    Computes the corner occupancy heuristic for the given board and player color.
    """
    c2 = 3 - color
    edge = [(0, 0), (0, len(board) - 1), (len(board) - 1, 0), (len(board) - 1, len(board) - 1)]
    e1 = sum(1 for x, y in edge if board[y][x] == color)
    e2 = sum(1 for x, y in edge if board[y][x] == c2)
    return 25 * (e1 - e2)

def corner_closeness_heuristic(board, color):
    """
    Computes the corner closeness heuristic for the given board and player color.
    """
    c2 = 3 - color
    s1, s2 = calculate_star_points(board, color, c2)
    return -12.5 * (s1 - s2)

def calculate_star_points(board, color, opponent_color):
    """
    Helper function to calculate star points around the corners for the given board and player color.
    """
    l = len(board)
    pts = [
        (0, 1), (1, 0), (1, 1),
        (0, l - 2), (1, l - 2), (1, l - 1),
        (l - 2, 0), (l - 2, 1), (l - 1, 1),
        (l - 2, l - 2), (l - 2, l - 1), (l - 1, l - 2)
    ]

    s1 = s2 = 0
    for x, y in pts:
        if board[y][x] == color:
            s1 += 1
        elif board[y][x] == opponent_color:
            s2 += 1
    return s1, s2

def stability_heuristic(board, color):
    """
    Placeholder for the stability heuristic for the given board and player color.
    """
    # Implementing a full stability heuristic is complex and requires a detailed analysis
    # of the board state to determine the stability of pieces.
    # This placeholder returns 0 for simplicity.
    return 0

def compute_heuristic(board, color):
    """
    Computes the overall heuristic value based on multiple factors.
    """
    p = parity_heuristic(board, color)
    m = mobility_heuristic(board, color)
    corner = corner_occupancy_heuristic(board, color)
    s = corner_closeness_heuristic(board, color)
    stab = stability_heuristic(board, color)

    # Adjust the weights as necessary based on game strategy and testing.
    heuristic_value = 4 * s + 8 * corner + p + 2 * stab + 0.5 * m
    return heuristic_value


def ordering_board(board, color, pos_move):
    b1 = dict()
    for i in pos_move:
        b2 = play_move(board, color, i[0], i[1])
        u1 = compute_heuristic(b2, color)
        b1.update({i: u1})

    u2 = sorted(b1.items(), key=lambda x: x[1], reverse=True)
    mov = [i[0] for i in u2]
    return mov


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    b = tuple(map(tuple, board))  # Convert board to a hashable type for caching
    if caching and (b in cach):
        return cach[b]

    c2 = 3 - color  # Switch player color
    moves = get_possible_moves(board, c2)
    if not moves or limit == 0:  # Check for terminal state or depth limit
        return None, compute_utility(board, color)

    min = float('inf')
    for i in moves:
        b2 = play_move(board, c2, i[0], i[1])
        _, utility = minimax_max_node(b2, color, limit - 1, caching)
        if utility < min:
            min, bestmove = utility, i

    if caching:
        cach[b] = (bestmove, min)

    return bestmove, min

def minimax_max_node(board, color, limit, caching=0):
    b = tuple(map(tuple, board))  # Convert board to a hashable type for caching
    if caching and (b in cach):
        return cach[b]

    moves = get_possible_moves(board, color)
    if not moves or limit == 0:  # Check for terminal state or depth limit
        return None, compute_utility(board, color)

    max = float('-inf')
    for move in moves:
        b2 = play_move(board, color, move[0], move[1])
        _, utility = minimax_min_node(b2, color, limit - 1, caching)
        if utility > max:
            max, bestmove = utility, move

    if caching:
        cach[b] = (bestmove, max)

    return bestmove, max

def select_move_minimax(board, color, limit, caching=0):
    cach.clear()  # Clear the cache at the start of each move selection
    mov, _ = minimax_max_node(board, color, limit, caching)
    return mov


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    board = tuple(map(tuple, board))
    if caching and (board in cach):
        return cach[board]

    if color == 1:
        c2 = 2
    else:
        c2 = 1

    best = None
    moves = get_possible_moves(board, c2)

    if not moves or limit == 0:
        return best, compute_utility(board, color)

    utility = float('inf')

    for i in moves:
        b2 = play_move(board, c2, i[0], i[1])
        mov2, u2 = alphabeta_max_node(b2, color, alpha, beta, limit - 1, caching, ordering)

        if caching:
            b2 = tuple(map(tuple, b2))
            cach.update({b2: (i, u2)})
        if utility > u2:
            utility, best = u2, i
        if utility <= alpha:
            return best, utility
        beta = min(beta, utility)

    return best, utility


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    board = tuple(map(tuple, board))
    if caching and (board in cach):
        return cach[board]

    best = None

    moves = get_possible_moves(board, color)

    if not moves or limit == 0:
        return best, compute_utility(board, color)

    u = -float('inf')

    if ordering:
        moves = ordering_board(board, color, moves)

    for i in moves:
        b2 = play_move(board, color, i[0], i[1])
        mov2, u2 = alphabeta_min_node(b2, color, alpha, beta, limit - 1, caching, ordering)

        if caching:
            b2 = tuple(map(tuple, b2))
            cach.update({b2: (i, u2)})
        if u < u2:
            u, best = u2, i
        if u >= beta:
            return best, u
        alpha = max(alpha, u)
    return best, u


def select_move_alphabeta(board, color, limit, caching=0, ordering=0):
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
    # IMPLEMENT (and replace the line below)
    cach.clear()
    alpha = -float('inf')
    beta = float('inf')
    mov, u = alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering)
    return mov



####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI")  # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0])  # Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1])  # Depth limit
    minimax = int(arguments[2])  # Minimax or alpha beta
    caching = int(arguments[3])  # Caching
    ordering = int(arguments[4])  # Node-ordering (for alpha-beta only)

    if (minimax == 1):
        eprint("Running MINIMAX")
    else:
        eprint("Running ALPHA-BETA")

    if (caching == 1):
        eprint("State Caching is ON")
    else:
        eprint("State Caching is OFF")

    if (ordering == 1):
        eprint("Node Ordering is ON")
    else:
        eprint("Node Ordering is OFF")

    if (limit == -1):
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1):
        eprint("Node Ordering should have no impact on Minimax")

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL":  # Game is over.
            print
        else:
            board = eval(input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1):  # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else:  # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()