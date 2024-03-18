#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

def corner_obs_deadlock(box, state):
    '''determine if box's x and y axis is next to a obstacle or wall'''
    '''INPUT: box, storage'''
    '''OUTPUT: True or False, True for corner deadlock'''

    deadlock_positions = state.obstacles.union(state.boxes)
    
    up = (box[0], box[1]-1) 
    down = (box[0], box[1]+1)
    left = (box[0]-1, box[1])
    right = (box[0]+1, box[1])

    if (up in deadlock_positions and left in deadlock_positions):
        return True
    if (up in deadlock_positions and right in deadlock_positions):
        return True
    if (down in deadlock_positions and left in deadlock_positions):
        return True
    if (down in deadlock_positions and right in deadlock_positions):
        return True 
    if (is_against_left_right_wall(box, state) and up in deadlock_positions):
        return True
    if (is_against_left_right_wall(box, state) and down in deadlock_positions):
        return True
    if (is_against_top_down_wall(box, state) and left in deadlock_positions):
        return True
    if (is_against_top_down_wall(box, state) and right in deadlock_positions):
        return True
    return False

def is_against_left_right_wall(box, state):
    '''determine if current box position is against left right wall or not'''
    '''INPUT: state, box'''
    '''OUTPUT: true or false'''
    return box[0]== 0 or box[0] == state.width - 1 

def is_against_top_down_wall(box, state):
    '''determine if current box position is against top down wall or not'''
    '''INPUT: state, box'''
    '''OUTPUT: true or false'''
    return box[1] == 0 or box[1] == state.height - 1

def is_deadlock(state, avaliable_box, avaliable_storage):
    '''only look at the boxes that are not in storage position already
    check 4 deadlock senario
    1. xy side is all wall
    2. xy side is a wall and a box, a wall and a obstacle, or a obstacle and obstacle, or a obstacle and a box or two box
    3. is next to verticle side of a wall and there is no storage on that side
    4. is next to horizonal side of a wall and there is no storage on that side
    true to indicate current position is in deadlock'''
    '''INPUT: state, avaliable_box, avaliable_storage'''
    '''OUTPUT: true or false'''
    for box in avaliable_box:
        if wall_corner_deadlock(box, state):
            return True
        elif corner_obs_deadlock(box, state):
            return True
        elif vertical_deadlock(box, state, avaliable_storage):
            return True
        elif horizontal_deadlock(box, state, avaliable_storage):
            return True
    return False

if 'prev_state' not in globals():
    prev_state = None
if 'prev_cal' not in globals():
    prev_cal = None

def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    ''' 1. check deadlock conditions, return directly
            a. 4 corners of wall
            b. xy obstructed by box and obstacle
            c. y obstructed by box and obstacle and left or right wall
            d. x obstructed by box and obstacle and top or down wall
            e. next to left right side wall with no storage on side
            f. next to top down side wall with no storage on side
        2. one storage position can only contain one box. so check for avaliable storage everytime
        3. precomputation. return directly if the same composition as before
        4. add in the computation for length from robot to box
        5. add in computation for obstruction, +2 for every obstruction on the route'''
    
    global prev_state
    global prev_cal

    if prev_state == state.boxes:
        return prev_cal
    else:
        prev_state = state.boxes
        
    avaliable_box = list(state.boxes - state.storage)
    avaliable_storage = list(state.storage - state.boxes)

    if is_deadlock(state, avaliable_box, avaliable_storage):
        prev_cal = math.inf
        return prev_cal
    else:
        prev_cal = heur_better_mahanttan_distance(state, avaliable_box, avaliable_storage)
        return prev_cal


def heur_better_mahanttan_distance(state, avaliable_box, avaliable_storage):
    '''determine the number of steps used for the better manhattan distance calculation
    include the distance from robot to box and also the obstacle step difference'''
    '''INPUT: state, avaliable_box, avaliable_storage'''
    '''OUTPUT: a numeric value that serves as an better estimate of the distance of the state to the goal'''
    total_dist = 0

    robot_to_box_dist = {}
    for box in avaliable_box:
        min_dist_from_robot = math.inf
        for robot in state.robots:
            robot_box_pair = (robot, box)
            if robot_box_pair not in robot_to_box_dist:
                robot_to_box_dist[robot_box_pair] = mahattan_distance(robot, box) + obstacle_count(robot, box, state)
            min_dist_from_robot = min(min_dist_from_robot, robot_to_box_dist[robot_box_pair])
        
        min_dist_to_storage = math.inf
        for storage in avaliable_storage:
            box_storage_pair = (box, storage)
            if box_storage_pair not in robot_to_box_dist:  
                robot_to_box_dist[box_storage_pair] = mahattan_distance(box, storage) + obstacle_count(box, storage, state)
            min_dist_to_storage = min(min_dist_to_storage, robot_to_box_dist[box_storage_pair])
        
        total_dist += min_dist_from_robot + min_dist_to_storage

    return total_dist

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    sum_dist = 0
    for box in state.boxes:
        dist = math.inf
        for storage in state.storage:
            dist = min(dist, mahattan_distance(box, storage))
        sum_dist += dist
    return sum_dist # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    fval = sN.gval + (weight * sN.hval)
    return fval #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    start_time = os.times()[4]
    end_time = os.times()[4] + timebound

    se = SearchEngine('custom', 'full')
    wrapped_fval_function = lambda sN: fval_function(sN, weight)
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)
    final, stats = se.search(timebound = (end_time - os.times()[4]), costbound=(math.inf, math.inf, math.inf))
    return final, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    end_time = os.times()[4] + timebound

    se = SearchEngine('custom', 'full')
    wrapped_fval_function = lambda sN: fval_function(sN, weight)
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)
    time_left = end_time - os.times()[4]
    best_result = 0
    first_search = True
    best_gval = math.inf
    
    while (time_left>0):
        #update cost[2] for iterative a* with gval
        found, stats = se.search(timebound = time_left, costbound=(math.inf, math.inf, best_gval))
        weight = weight * 0.5
        if found == False:
            if (first_search):
                return found, stats
        else:
            if (best_gval > found.gval):
                best_gval = found.gval
                best_result = found, stats
        first_search = False
        time_left = end_time - os.times()[4]
    return best_result[0], best_result[1] #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    end_time = os.times()[4] + timebound

    se = SearchEngine('best_first', "full")
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=fval_function)
    best_gval = math.inf
    time_left = end_time - os.times()[4]
    best_result = 0
    first_search = True

    while (time_left>0):
        #update cost[0] for gbfs with gval
        found, stats = se.search(timebound=time_left, costbound=(best_gval, math.inf, math.inf))
        if found == False:
            if(first_search):
                return found, stats
        else:
            if (best_gval > found.gval):
                best_gval = found.gval
                best_result = found, stats
        first_search = False
        time_left = end_time - os.times()[4]
    return best_result[0], best_result[1] #CHANGE THIS

def mahattan_distance(box, storage):
    '''calculate mahattan distance between box and storage'''
    '''INPUT: box, storage'''
    '''OUTPUT: distance between box and storage'''
    distance = 0
    distance += abs(box[0] - storage[0]) + abs(box[1]-storage[1])
    return distance       


def wall_corner_deadlock(box, state):
    '''calculate if current location is one of the corners'''
    '''INPUT: box, state'''
    '''OUTPUT: true or false'''
    corner_positions = [(0,0), (0,state.height-1), (state.width-1, 0), (state.width-1, state.height-1)]

    if box in corner_positions:
        return True
        # Enhanced obstacle and edge consideration
    return False

def horizontal_deadlock(box, state, avaliable_storage):
    '''determine if there is a wall on the left or right side of the box and there is no avaliable storage on the column'''
    '''INPUT: box, state, avaliable storage'''
    '''OUTPUT: true or false'''
    if (box[0] == 0):
        if (not(any(st[0] == 0 for st in avaliable_storage))):
            return True
        
    if (box[0] == state.width-1):
        if (not(any(st[0] == state.width-1 for st in avaliable_storage))):
            return True
    return False

def vertical_deadlock(box, state, avaliable_storage):
    '''determine if there is a wall on the top or bottom side of the box and there is no goal on the row'''
    '''INPUT: box, state, avaliable storage'''
    '''OUTPUT: true or false'''
    if (box[1] == 0):
        if (not(any(st[1] == 0 for st in avaliable_storage))):
            return True
        
    if (box[1] == state.height-1):
        if (not(any(st[1] == state.height-1 for st in avaliable_storage))):
            return True
    return False

def obstacle_count(box, position, state):
    '''determine the distance from robot to box. consider obstacle + 2 in steps. if there is no obstacle get from 
    (0,0) to (0,2) in 2 steps. if there is obstacle at (0,1), need 4 steps to go from (0,0) to (1,0) and 
    (1,0) to (1,1), (1,1) to (1,2), (1,2) to (0,2). so when there is obstacle, step +2.'''
    '''INPUT: box, postition, state'''
    '''OUTPUT: number of more steps because of obstacle'''
    obstacle_list = list(state.boxes) + list(state.obstacles) + list(state.robots)

    if (box in obstacle_list):
        obstacle_list.remove(box)

    if (position in obstacle_list):
        obstacle_list.remove(position)

    m_path = manhattan_path(box, position)
    obstacle_count = sum (2 for element in m_path if element in obstacle_list)
    return obstacle_count

def manhattan_path(position1, position2):
    '''return a list of every point on the manhattan path'''
    '''INPUT: point1, point2'''
    '''OUTPUT: list of points on the path'''
    path = [position1]

    if (position2[0]> position1[0]):
        dir_x = 1
    else:
        dir_x = -1
    
    if (position2[1]> position1[1]):
        dir_y = 1
    else:
        dir_y = -1

    for x in range(position1[0], position2[0], dir_x):
        path.append((x + dir_x, position1[1]))

    for y in range(position1[1], position2[1], dir_y):
        path.append((position2[0], y + dir_y))

    return path