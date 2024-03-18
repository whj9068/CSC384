# Save this file as whatever.py in your assignment 1 directory, and run this file

# credit: chatgpt. 
# https://chat.openai.com/share/a713d16c-4379-462d-a601-fab9e613eb8f

from solution import *
from sokoban import sokoban_goal_state, PROBLEMS

HEURISTIC_FUNC = heur_alternate

def parse_state_string(state_string):
  lines = state_string.strip().split('\n')
  height = len(lines) - 2  # Excluding walls
  width = len(lines[0]) - 2  # Excluding walls

  robots = {}
  boxes = frozenset()
  storage = frozenset()
  obstacles = frozenset()

  for y, line in enumerate(lines):
      for x, char in enumerate(line):
          if char == '.':
              storage = storage.union({(x - 1, y - 1)})
          elif char == '#':
              if 0 < x < len(line) - 1 and 0 < y < len(lines) - 1:  # Ignore outer walls
                  obstacles = obstacles.union({(x - 1, y - 1)})
          elif char == '$':
              boxes = boxes.union({(x - 1, y - 1)})
          elif char == '*':
              boxes = boxes.union({(x - 1, y - 1)})
              storage = storage.union({(x - 1, y - 1)})
          elif 'a' <= char <= 'z':
              robots[char] = ((x - 1, y - 1))
          elif 'A' <= char <= 'Z':
              robots[char.lower()] = ((x - 1, y - 1))
              storage = storage.union({(x - 1, y - 1)})

  # Assuming 'action', 'gval', and 'parent' can be initialized with default or null values
  robots = sorted(robots.items())
  robots = [ t for _, t in robots]
  return SokobanState("START", 0, None, width, height, tuple(robots), boxes, storage, obstacles)


def test():
  s = PROBLEMS[0]
  s2 = parse_state_string(s.state_string())
  for k,v in s.__dict__.items():
    print(k,v)
  for k,v in s2.__dict__.items():
    print(k,v)
  print(s2.state_string() ==s.state_string())
def verify_inverse(s):
  s2 = parse_state_string(s.state_string())
  return (s2.state_string() ==s.state_string())

from collections import deque

from tqdm import tqdm

def bfs(initial_state, max_states=100000000):
  visited = {initial_state.hashable_state()}
  queue = deque([initial_state])  # Queue of state and path pairs
  i=0
  with tqdm() as pbar:
    while queue:
      i+=1
      if i==max_states: 
        return True, "MAX"
      if i%(max_states//1000)==0: pbar.update(max_states//100)
  
      current_state = queue.popleft()
      if verify_inverse(current_state)==False: return False, current_state
      for neighbor in current_state.successors():
        nh=neighbor.hashable_state()
        if nh not in visited:
          queue.append(neighbor)
          visited.add(nh)
  
  return True, i

import math


def VERIFY():
  result_list = []
  for i in range(22):
    p = PROBLEMS[i]
    n = p.width*p.height
    r = len(p.boxes)+len(p.robots)
    ways_to_distribute = math.perm(n , r)
    result, s = bfs(p)
    print(ways_to_distribute,s)
    try:
      print(s/ways_to_distribute)
    except:
      pass
    result_list.append(s)
    if result!=True:
      print()
      print(s.state_string())
      print()
      s2 = parse_state_string(s.state_string())
      print(s2.state_string())
      for k,v in s.__dict__.items():
        print(k,v)
      for k,v in s2.__dict__.items():
        print(k,v)
  print(result_list)


DEAD = """
#######
#* #$ #
#b #  #
#.    #
#  #a #
#* #  #
#######

#######
#* # $#
#b #  #
#.    #
#  #a #
#* #  #
#######

#######
#. #  #
#b # $#
#.   $#
#  #a #
#* #  #
#######

#######
#. #$$#
#b #  #
#.    #
#  #a #
#* #  #
#######

#######
#. #$ #
#b #$ #
#. $  #
#  #a #
#. #  #
#######

########
#      #
# $A.$ #
# $B. $#
#      #
########

########
#     .#
# $A  $#
# $B  $#
#     .#
########

########
#     .#
# $A  *#
# $B  $#
#      #
########

#######
# ###.#
#$  a$#
#     #
#  b$ #
#.###.#
#######

#######
#*###.#
#$  a$#
#     #
#  b$ #
#.###.#
#######

#######
#*###.#
#$  a$#
#     #
#  b  #
#*###.#
#######

#######
#.###.#
# $ $ #
#  a  #
#    $#
#.###*#
#######

########
#      #
#  A   #
#  b  $#
#      #
########

########
#     $#
#  A   #
#  b   #
#      #
########

########
#      #
#  A$$ #
#  b$$ #
#  ... #
########

########
#      #
#  A$$ #
#  b$$$#
# .... #
########

########
#      #
#  A   #
#  b$$$#
# ..  *#
########

########
#      #
#  A   #
#  b  $#
#     *#
########

########
#     .#
#  a   #
#  b  $#
#     *#
########

#######
#.*# a#
#$ #  #
#. $  #
#  #$ #
#. # b#
#######

#######
#.*# a#
#$*#  #
#. $  #
#  #$ #
#. # b#
#######

########
#a$   .#
#      #
#b    .#
#      #
#c    $#
#.   $ #
########

########
#.$    #
#$.    #
#      #
#      #
# $ $ B#
#    cA#
########

##########
#...     #
#..      #
#.       #
#     $$ #
#     $$ #
#a    $$ #
# b      #
#  c     #
##########
""".strip()

ALIVE = """
##########
#...     #
#..      #
#.   $   #
#     $$ #
#     $  #
#a    $$ #
# b      #
#  c     #
##########

########
#.*    #
#$.    #
#      #
#      #
# $ $ b#
#    cA#
########

########
#a$   .#
#      #
#b$   .#
#      #
#c$    #
#.     #
########

########
#a$   .#
#      #
#b$   .#
#      #
#c    $#
#.     #
########

#######
#. # a#
#  #$ #
#. $  #
#  #$ #
#. # b#
#######

#######
#. # a#
#$ #  #
#. $  #
#  #$ #
#. # b#
#######

########
#      #
#  A$  #
#  b   #
#      #
########


########
#     .#
#  a  $#
#  b   #
#     *#
########

########
#      #
# $A.$ #
# $B.$ #
#      #
########

########
#      #
# $A.$ #
# $B.$ #
#    $.#
########

#######
#.###.#
# $a$ #
#     #
# $b$ #
#.###.#
#######

#######
#.###*#
# $   #
#  a  #
# $  $#
#.###.#
#######

#######
#.###.#
# $  $#
#  a  #
# $  $#
#.###.#
#######

#######
#.###.#
# $a$ #
#     #
# $b $#
#.###.#
#######

#######
#.###.#
#$ a$ #
#     #
# $b $#
#.###.#
#######

#######
#.###.#
#$ a $#
#     #
#$ b $#
#.###.#
#######

#######
#.###.#
#$$a  #
#     #
#$ b $#
#.###.#
#######

########
#     .#
# $A $ #
# $B. $#
#      #
########

#######
#.a#* #
#b #  #
#  $  #
#  #  #
#  #  #
#######

#######
#  #. #
#b #a #
#  $$ #
#  #  #
#  #. #
#######

#######
#. #. #
#b #a #
# $$$ #
#  #  #
#  #. #
#######

"""

DEADSTATES = []
for statestr in DEAD.split("\n\n"):
  s =parse_state_string(statestr.strip())
  assert (len(s.boxes)==len(s.storage))
  DEADSTATES.append(s)

ALIVESTATES = []
for statestr in ALIVE.split("\n\n"):
  s =parse_state_string(statestr.strip())
  assert (len(s.boxes)==len(s.storage))
  ALIVESTATES.append(s)

if __name__ == "__main__":
  for s in DEADSTATES:
    if HEURISTIC_FUNC(s) != float('inf'):
      print("FOUND ISSUE: state is DEAD and should be inf, but your h =",HEURISTIC_FUNC(s))
      print(s.state_string())
  for s in ALIVESTATES:
    if HEURISTIC_FUNC(s) == float('inf'):
      print("FOUND ISSUE: state is ALIVE, but your h =",HEURISTIC_FUNC(s))
      print(s.state_string())