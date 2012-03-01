from copy import deepcopy
from backtracking import *
from random import choice, sample

class MaxIterationsExceeded(Exception) : pass

# Determines whether or not a variable is conflicted
def is_conflicted(var, assignment, csp):
    for c in csp.constraints(var):
        if not c.is_satisfied(assignment):
            return True
    return False

# The minconflicts algorithm
def minconflicts(csp, max_steps = 1000000, assignment = None):

    # The variables are integers
    variables = [i for i in range(len(csp.X))]

    if assignment:
        # Make sure the initial assignment is complete
        if not is_complete(assignment):
            raise ValueError('minconflicts must be given a complete assigment.')
        else:
            # Make a copy of the assignment
            current = deepcopy(assignment)

    # If we weren't given an inital assignment then generate a random one
    else:
        current = [0]*len(csp.X)
        for i in variables:
            current[i] = sample(csp.D[i], 1)[0]

    # Conflicts returns the total number of conflicted variables in a
    def conflicts(a): return reduce(lambda accu, x : accu + is_conflicted(x, a, csp), variables)
    
    # Try to find a consistent solution
    for i in range(max_steps):

        print current

        # If this is a correct assignment return it.
        if reduce(lambda accu, x : accu and not is_conflicted(x, current, csp), variables, True):
            print 'Found solution'
            return current

        # Otherwise pick a random conflicted variable
        var = choice(filter(lambda x : is_conflicted(x, current, csp), variables))

        # Find the value for var that minimizes the number of conflicts
        min_conflicts = conflicts(current)
        min_value = current[var]
        for value in csp.D[var]:
            current[var] = value
            c = conflicts(current) 
            print c
            if c < min_conflicts:
                min_conflicts = c
                min_value = value

        # Set var to be the value that minimizes conflicts
        current[var] = value

    raise MaxIterationsExceeded