import unittest
import sys
import itertools
import traceback

from cspbase import *
from puzzle_csp import *
from propagators import *
import propagators
def queensCheck(qi, qj, i, j):
    '''Return true if i and j can be assigned to the queen in row qi and row qj
       respectively. Used to find satisfying tuples.
    '''
    return i != j and abs(i-j) != abs(qi-qj)

def nQueens(n):
    '''Return an n-queens CSP'''
    i = 0
    dom = []
    for i in range(n):
        dom.append(i+1)

    vars = []
    for i in dom:
        vars.append(Variable('Q{}'.format(i), dom))

    cons = []
    for qi in range(len(dom)):
        for qj in range(qi+1, len(dom)):
            con = Constraint("C(Q{},Q{})".format(qi+1,qj+1),[vars[qi], vars[qj]])
            sat_tuples = []
            for t in itertools.product(dom, dom):
                if queensCheck(qi, qj, t[0], t[1]):
                    sat_tuples.append(t)
            con.add_satisfying_tuples(sat_tuples)
            cons.append(con)

    csp = CSP("{}-Queens".format(n), vars)
    for c in cons:
        csp.add_constraint(c)
    return csp

TEST_PROPAGATORS = True
class TestStringMethods(unittest.TestCase):
    @unittest.skipUnless(TEST_PROPAGATORS, "Not Testing Propagotors.")
    def test_DWO_FC(self):
        queens = nQueens(6)
        cur_var = queens.get_all_vars()
        cur_var[0].assign(2)
        pruned = propagators.prop_FI(queens,newVar=cur_var[0])
        self.assertTrue(pruned[0], "Failed a FC test: returned DWO too early.")
        cur_var[1].assign(5)
        pruned = propagators.prop_FI(queens,newVar=cur_var[1])
        self.assertTrue(pruned[0], "Failed a FC test: returned DWO too early.")

if __name__ == '__main__':
    unittest.main()