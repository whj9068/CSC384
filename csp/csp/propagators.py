#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.  

'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

   '''

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''
    
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with 
       only one uninstantiated variable. Remember to keep 
       track of all pruned variable,value pairs and return '''
    #IMPLEMENT
    pruned = []
    
    if not newVar:
        #we forward check all constraints with V that have one unassigned variable left
        constraints = csp.get_all_cons()
    else:
        #we forward check all constraints with V that have one unassigned variable left
        constraints = csp.get_cons_with_var(newVar)

    for c in constraints:
        #check constraints with only one uninstantiated variable
        if c.get_n_unasgn() == 1:
            unasgn_var = c.get_unasgn_vars()[0]
            #go through current domain for selected unassigned variable
            #for d:= each member of CurDom[x]
            for d in unasgn_var.cur_domain():
                vals = []
                #assign value
                unasgn_var.assign(d)
                vars = c.get_scope()
                for var in vars:
                    vals.append(var.get_assigned_value())

                #if making x=d together with previous assignments to variables in scope c falsifies C
                #remove d from CurDom[V]
                if not c.has_support(unasgn_var,d):
                    unasgn_var.prune_value(d)
                    pruned.append((unasgn_var, d))

                #restore
                unasgn_var.unassign()              
                
                #domain wipe out
                if unasgn_var.cur_domain_size()==0:
                    return False, pruned
                
    return True, pruned

        
    

def prop_FI(csp, newVar=None):
    '''Do full inference. If newVar is None we initialize the queue
       with all variables.'''
    #IMPLEMENT
    #initialization of variable queue and pruned queue
    var_queue = []
    pruned = []
    if not newVar:
        #initialize the queue with all variable if newVar is none
        for v in csp.get_all_unasgn_vars():
            if v not in var_queue:
                var_queue.append(v)
    else:
        #var queue only contains newVar if newVar specified
        var_queue.append(newVar)

    #while VarQueue is not empty
    while var_queue:
        #extract the first element in queue
        unasgn_var = var_queue.pop(0)
        #For each constraints C where W is in scope of C
        for c in csp.get_cons_with_var(unasgn_var):
            #for each member of scope C that is not W
            for v in c.get_scope():
                if v != unasgn_var:
                    changed = False
                    #for each member of curDom of V
                    for d in v.cur_domain():
                        #get their assign value
                        vals = []
                        vars = c.get_scope()
                        for var in vars:
                            vals.append(var.get_assigned_value())
                        
                        #find an assignment A for all other variables in scope(C) such that C(AUV=d) is true
                        #if A not found, remove d from the domain of V
                        if not c.has_support(v, d):
                            changed = True
                            v.prune_value(d)
                            pruned.append((v, d))
                            
                            #DWO for V, return immediately
                            if v.cur_domain_size() == 0:
                                return False, pruned
                            
                    #if domain of V has changed
                    if changed:
                        #append if not in already
                        if v not in var_queue:
                            var_queue.append(v)

    return True, pruned
     
            


    