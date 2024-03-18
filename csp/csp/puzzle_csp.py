#Look for #IMPLEMENT tags in this file.
'''
All encodings need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = caged_csp(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only encodings do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. caged_csp (worth 25/100 marks) 
    - An enconding built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.

'''
from cspbase import *
import itertools
import math

def binary_ne_grid(fpuzz_grid):
    ##IMPLEMENT
    domain = []
    grid_size = fpuzz_grid[0][0]

    #initialize domain. domain is from 1 to gridsize
    for i in range(grid_size):
        domain.append(i+1)
    
    #initialize variable ie row 0 col 0 is C11 based on definition
    var_list = []
    for r in range(grid_size):
        row = []
        for c in range(grid_size):
            variable_grid = Variable('Variable{}{}'.format(r+1, c+1), domain)
            row.append(variable_grid)
        var_list.append(row)
    
    #initialize constraint
    #V1i ≠ V2i, V1i ≠ V3i, and V2i ≠ V3i
    #Vi1 ≠ Vi2, Vi1 ≠ Vi3, and Vi2 ≠ Vi3
    constraint_list = []
    for i in range(grid_size):
        for j in range(grid_size):
            #Vi1 ≠ Vi2, Vi1 ≠ Vi3, and Vi2 ≠ Vi3
            for k in range(j+1, grid_size): 
                con_row = Constraint("Constraint(Variable{}{},Variable{}{})".format(i+1,j+1,i+1,k+1), [var_list[i][j], var_list[i][k]])
                sat_tuples = []
                #find tuple where two numbers are not equal. append
                for x, y in itertools.product(domain, domain):
                    if x != y:
                        sat_tuples.append((x, y))                
                con_row.add_satisfying_tuples(sat_tuples)
                constraint_list.append(con_row)

        
        for j in range(grid_size):
            for k in range(j+1, grid_size): 
                #V1i ≠ V2i, V1i ≠ V3i, and V2i ≠ V3i
                con_col = Constraint("Constraint(Variable{}{},Variable{}{})".format(j+1, i+1, k+1, i+1), [var_list[j][i], var_list[k][i]])
                sat_tuples = []
                #find tuple where two numbers are not equal. append
                for x, y in itertools.product(domain, domain):
                    if x != y:
                        sat_tuples.append((x, y))                 
                con_col.add_satisfying_tuples(sat_tuples)
                constraint_list.append(con_col)
    
    csp = CSP("binary_ne_grid")
    
    #add var to csp
    for row in var_list:
        for v in row:
            csp.add_var(v)
    
    #add constraints to csp
    for c in constraint_list:
        csp.add_constraint(c)
    
    return csp, var_list

        

def nary_ad_grid(fpuzz_grid):
    ##IMPLEMENT
    domain = []
    grid_size = fpuzz_grid[0][0]

    #initialize domain. domain is from 1 to gridsize
    for i in range(grid_size):
        domain.append(i+1)
    
    #initialize variable ie row 0 col 0 is C11 based on definition
    var_list = []
    for r in range(grid_size):
        row = []
        for c in range(grid_size):
            variable_grid =Variable('Variable{}{}'.format(r+1, c+1), domain)
            row.append(variable_grid)
        var_list.append(row)
    
    #initialize constraint
    constraint_list = []
    #constraint restrict over the whole row
    for r in range(grid_size):
        #row constraints
        row_list = var_list[r]
        con = Constraint("Constraint(Row{})".format(r+1), row_list)
        sat_tuples = []
        #every cell on the row should have different value choosing from domain.
        #use permutation because 123 different from 132
        for t in itertools.permutations(domain, len(domain)):
            sat_tuples.append(t)
        con.add_satisfying_tuples(sat_tuples)
        constraint_list.append(con)

    #constraint restrict over the whole column
    for c in range(grid_size):
        #column constraints
        col_list = []
        for r in range (grid_size):
            col_list.append(var_list[r][c])
        con = Constraint("Constraint(Column{})".format(c+1), col_list)
        sat_tuples = []
        #every cell on the column should have different value choosing from domain.
        #use permutation because 123 different from 132
        for t in itertools.permutations(domain, len(domain)):
            sat_tuples.append(t)
        con.add_satisfying_tuples(sat_tuples)
        constraint_list.append(con)
    
    csp = CSP("nary_ad_grid")
    
    #add var to csp
    for row in var_list:
        for variable in row:
            csp.add_var(variable)

    #add constraints to csp
    for c in constraint_list:
        csp.add_constraint(c)
    
    return csp, var_list 
    

def caged_csp(fpuzz_grid):
    ##IMPLEMENT 
    domain = []
    grid_size = fpuzz_grid[0][0]

    #initialize domain. domain is from 1 to gridsize
    for i in range(grid_size):
        domain.append(i+1)
    
    #encoding built from binary_ne_grid
    csp, var_list = binary_ne_grid(fpuzz_grid)

    #initialize constraint
    constraint_list = []
    index = 0
    #traverse through each cage in the grid
    for cage in fpuzz_grid[1:]:
        #the case where there is no operation, just cell and target value
        if len(cage) == 2:
            #extract row and column
            cell, value = cage
            row = (cell // 10) - 1 
            col = (cell % 10) - 1 
            cage_cons = Constraint("Constraint(Cage{})".format(index), [var_list[row][col]])
            #add target value in
            sat_tuples = [(value,)] 
            cage_cons.add_satisfying_tuples(sat_tuples)
            constraint_list.append(cage_cons)
        else:
            #extract cell, target, operation
            cells, target, operation = cage[:-2], cage[-2], cage[-1]
            cell_vars = []
            #extract row and column
            for i in cells:
                col = (i % 10) - 1 
                row = (i // 10) - 1
                cell_vars.append(var_list[row][col])
            
            cage_cons = Constraint("Constraint(Cage{})".format(index), cell_vars)
            #add satisfying tuple based on operation used
            if operation == 0:
                #+
                sat_tuples = get_satisfying_tuples_for_addition(cell_vars, target, domain)
            elif operation == 1:
                #-
                sat_tuples = get_satisfying_tuples_for_subtraction(cell_vars, target, domain)
            elif operation == 2:
                #/
                sat_tuples = get_satisfying_tuples_for_division(cell_vars, target, domain)
            elif operation == 3:
                #*
                sat_tuples = get_satisfying_tuples_for_multiplication(cell_vars, target, domain)
                
            cage_cons.add_satisfying_tuples(sat_tuples)
            constraint_list.append(cage_cons)

        index = index + 1

    #add constraints to csp
    for c in constraint_list:
        csp.add_constraint(c)
        
    return csp, var_list


def get_satisfying_tuples_for_addition(variables, target, domain):
    satisfying_tuples = []
    # Generate all combinations of the domain, with count equal to the length of variable_list
    for combo in itertools.product(domain, repeat=len(variables)):
        #get the sum of combo and check if its the same value as target or not
        if sum(combo) == target:
            satisfying_tuples.append(combo)    
    return satisfying_tuples


import itertools

def get_satisfying_tuples_for_subtraction(variable_list, desired_result, domain):
    solutions = []
    # Generate all combinations of the domain, with a count equal to the length of variable_list
    for combination in itertools.product(domain, repeat=len(variable_list)):
        # Order matters because subtraction is left associative
        # Initialize subtraction with the first element
        subtraction_result = combination[0]
        # Subtract all subsequent elements from the initial element
        for value in combination[1:]:
            subtraction_result -= value
        # If the result matches the desired result, store the combination
        if subtraction_result == desired_result:
            solutions.append(combination)
    
    final_solutions = set()
    # Generate all unique permutations of each combination that resulted in the desired outcome
    for combination in solutions:
        for permutation in itertools.permutations(combination):
            final_solutions.add(permutation)
    
    return list(final_solutions)


def get_satisfying_tuples_for_multiplication(variables, target, domain):
    satisfying_tuples = []
    # Generate all combinations of the domain, with count equal to the length of variable_list
    for combo in itertools.product(domain, repeat=len(variables)):
        #get the product of combo and check if its the same value as target or not
        if math.prod(combo) == target:
            satisfying_tuples.append(combo)    
    return satisfying_tuples


def get_satisfying_tuples_for_division(variable_list, desired_result, domain):
    solutions = []
    # Generate all combinations of the domain, with count equal to the length of variable_list
    for combination in itertools.product(domain, repeat=len(variable_list)):
        division_head = combination[0]
        valid_combination = True
        # Divide all subsequent elements from the initial element
        for value in combination[1:]:
            if value == 0:  # Cannot divide by 0
                valid_combination = False
                break  # Skip this combination entirely if any value is 0
            else:
                division_head /= value
        # Check if it matches the target and is valid (no division by 0 encountered)
        if valid_combination and division_head == desired_result:
            solutions.append(combination)
    
    final_solutions = set()
    # Generate all unique permutations of each combination that resulted in the desired outcome
    for combination in solutions:
        for permutation in itertools.permutations(combination):
            final_solutions.add(permutation)
  
    return list(final_solutions)
