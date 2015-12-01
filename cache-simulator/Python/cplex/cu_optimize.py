import numpy as np
import cplex
from cplex import Cplex
from cplex.exceptions import CplexError

capacity = 100  # Capacity of the cache
k = 2  # Number of items
n = 5  # Number values for each item
profit = [[5, 10, 40, 40, 40],
          [5, 10, 25, 30, 30]]
weight = [10, 20, 50, 70, 80]

xvar = [ [ 'x'+str(i)+str(j) for j in range(1,n+1) ] for i in range(1,k+1) ]
xvar = xvar[0] + xvar[1]
profit = profit[0] + profit[1]

types = 'B'*n*k

ub = [1]*n*k
lb = [0]*n*k

try:
    prob = cplex.Cplex()
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj = profit, lb = lb, ub = ub, types = types, names = xvar )

    rows = [[ xvar, weight+weight ]]
    rows = [[ xvar, weight+weight ],
            [ xvar[:5], [1]*5 ],
            [ xvar[5:], [1]*5 ],
           ]

    prob.linear_constraints.add(lin_expr = rows, senses = 'LEE', rhs = [capacity,1,1], names = ['r1','r2','r3'] )

    prob.solve()
    print
    print "Solution value  = ", prob.solution.get_objective_value()
    xsol = prob.solution.get_values()
    print 'xsol = ', np.reshape(xsol, (k,n) )

except CplexError as exc:
    print(exc)
