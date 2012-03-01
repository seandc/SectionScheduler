from collections import namedtuple
from cs1_assignment import cs1_assignment
import sys
from copy import deepcopy

# Generates some tables that will allow faster lookup in the CSP
def generate_maps(X, C):

    # Initialize the tables
    n = len(X)
    var_to_constraints = [[] for i in range(n)]
    set_to_constraint = {}
    var_to_neighbors = [set() for i in range(n)]

    # Build the maps:
    for c in C:
        key = frozenset(c.vars)
        set_to_constraint[key] = c

        for v1 in c.vars:

            # Add the constraint to v1's list
            var_to_constraints[v1].append(c)

            # Add v1's neighbors to it's neighbor set
            for v2 in c.vars:
                if v2 != v1:
                    var_to_neighbors[v1].add(v2)

    # Return the computed tables
    return var_to_constraints, set_to_constraint, var_to_neighbors


class CSP(object):
    def __init__(self, X, D, C):

        # The variables - a list of strings
        self.X = X

        # The domains - contains a set of values for each variable in X
        self.D = D

        # The constraints - each constraint is a set and a function
        self.C = C

        # There are three tables that are used to speed things up
        self.var_to_constraints, self.set_to_constraint, self.var_to_neighbors = generate_maps(self.X, self.C)

    # The following three functions are used to 
    # make the table lookups more readable:

    # Function that takes a variable and returns
    # that variables neighbors as a set
    def neighbors(self, var):
        return self.var_to_neighbors[var]

    # Function that takes a variable and returns
    # the contraints it is involved in 
    def constraints(self, var):
        return self.var_to_constraints[var]

    # Takes a set of variables and returns the 
    # constraint that connects them
    def constraint(self, vs):
        return self.set_to_constraint[vs]


# CSP = namedtuple('CSP', ['X', 'D', 'C'])

constraint = namedtuple('constraint', ['vars', 'is_satisfied'])

def is_complete(assignment):
    #return not any(map(lambda x : x == None, assignment))
    return reduce(lambda accu, x : accu and (x != None), assignment, True)

# def check_constraint(constraint, assignment):
#    return constraint.is_satisfied(assignment)

def is_consistent(var, value, assignment, csp):
    assignment[var] = value

    for c in csp.constraints(var):
        if not c.is_satisfied(assignment):
            assignment[var] = None
            return False

    #result = all([check_constraint(constraint, assignment) for constraint in csp.C])
    assignment[var] = None
    return True
    #return result

def count_legal_values(var, csp, assignment):
    count = 0
    for value in csp.D[var]:
        if is_consistent(var, value, assignment, csp):
            count += 1
    return count

def mrv(csp, assignment):
    return min([(count_legal_values(var, csp, assignment), var) for var in range(len(csp.X)) if assignment[var] == None])[1]

def lcv(var, assignment, csp):
    score_value_pairs = []
    for value in csp.D[var]:
        assignment[var] = value
        total = 0
        for neighbor in csp.neighbors(var):
            if assignment[neighbor] == None:
                total += count_legal_values(neighbor, csp, assignment)
        score_value_pairs.append((total, value))
        assignment[var] = None
    return map(lambda (score, value): value, sorted(score_value_pairs))

def first_unassigned(csp, assignment):
    for i in range(len(assignment)):
        if assignment[i] == None:
            return i
    raise ValueError('The assignment is complete: ' + str(assignment))

def order_domain_values(var, assignment, csp):
    return csp.D[var]

# The maintain arc consistency inference algorithm. Code is based on the AC-3
# code from the textbook. It usually doesn't seem to speed up search very much
# but the results are still correct.
def mac(csp, assignment, var, value):

    domain = deepcopy(csp.D)
    a = deepcopy(assignment)

    def revise(i, j):

        # Get the constraint for this pair
        c = csp.constraint(frozenset([i, j]))

        revised = False

        to_be_removed = set()
        for x in domain[i]:
            a[i] = x

            satisfied = False
            # Look for a value of y that is consistent
            for y in domain[j]:
                a[j] = y

                # If we find a y that satisfies 
                # the constraint we break and 
                # reset a[j]
                if c.is_satisfied(a):
                    a[j] = None
                    satisfied = True
                    break

                # Reset a[j]
                a[j] = None

            # If we made it through the loop then x is 
            # not a possible value. Remove it from the doman.
            if not satisfied:
                to_be_removed.add(x)
                revised = True

            # Reset a[i]
            a[i] = None
            
        domain[i] -= to_be_removed
        return revised

    # Add all of the arcs for this csp to another set
    arcs = [(var, i) for i in csp.neighbors(var) if assignment[i] == None]
    arcs += [(y, x) for (x, y) in arcs]
    arcs = set(arcs)

    while arcs:
        i, j = arcs.pop()
        if revise(i, j):
            if len(domain[i]) == 0:
                return None
            else:
                for var in csp.neighbors(i):
                    if var != j:
                        arcs.add((var, i))

    inferences = {}
    for var in range(len(csp.X)):
        if len(domain[var]) == 1:
            value = domain[var].pop()
            inferences[var] = (value, assignment[var])
    return inferences

# A custom exception that can be thrown if the constraints can't be satisifed
class CannotBeSatisfied(Exception): pass

def backtracking_search(csp, select_unassigned_variable, order_domain_values, inference, special_assignment = None):

    def backtrack(assignment):

        # If the assigment is complete, return it.
        if is_complete(assignment): 
            return assignment 

        # Choose an unsassigned variable
        var = select_unassigned_variable(csp, assignment)

        # Try the different values in the domain
        for value in order_domain_values(var, assignment, csp):

            # Initalize inferences to be nothing
            inferences = None

            # If the assignment of value to var is consistent
            # then try to make more assignments using inference
            # and continue backtracking.
            if is_consistent(var, value, assignment, csp):
                assignment[var] = value
                inferences = inference(csp, assignment, var, value)

                # If the inference was succesful then assign
                # the inferred values. Otherwise, this assignment
                # is a deadend and we move on to the next value.
                if inferences != None:
                    for var in inferences:
                        assignment[var] = inferences[var][0]

                    # Continue backtracking with the new assignment
                    result = backtrack(assignment)

                    # If we found a consistent and complete 
                    # assigment, return it.
                    if result != None:
                        return result

            # Unasign the variable
            assignment[var] = None

            # If the inference was succesful then remove
            # the inferred values from the the assignment
            if inferences != None:
                for var in inferences:
                    assignment[var] = inferences[var][1]

        # Failed to make a complete and consistent assignment
        return None

    # If a special assignment was given then start running the algorithm
    # on the special assignment
    if special_assignment:
        result = backtrack(special_assignment)

    # Otherwise, start the backtracking search with an empty assignment
    else:
        result = backtrack(len(csp.X)*[None])

    # Return the assigment if the search was succesful
    if result:
        return result

    # Otherwise raise an exception
    else:
        raise CannotBeSatisfied()

# Backtracking with no heuristics and no inference.
def standard_bt(csp):
    return backtracking_search(csp, first_unassigned, order_domain_values, lambda w, x, y, z: {})

# Backtracking with MRV heuristic. Usually the fastest by far on circuit problems.
def bt_with_mrv(csp):
    return backtracking_search(csp, mrv, order_domain_values, lambda w, x, y, z : {})

# Backtracking with the mac inference. Doesn't speed up search much (but is not as bad as lcv)
def bt_with_mac(csp):
    return backtracking_search(csp, first_unassigned, order_domain_values, mac)

# Backtracking with mrv and lcv. This was usually the slowest (other than complete).
def bt_with_mrv_and_lcv(csp):
    return backtracking_search(csp, mrv, lcv, lambda w, x, y, z : {})

# Backtracking with the mrv heuristic and mac inference. Not an improvment over standard_bt.
def bt_with_mrv_and_mac(csp):
    return backtracking_search(csp, mrv, order_domain_values, mac)

# Backtracking with all the additions.
def complete_bt(csp):
    return backtracking_search(csp, mrv, lcv, mac)

# This is the backtracking with no heuristics. It uses a special class to allow
# for fast consistency checking.
def standard_bt_with_cs1_data(csp, leaders, times):
    assignment = cs1_assignment(len(csp.X), leaders, times)
    return backtracking_search(csp, first_unassigned, order_domain_values, lambda w, x, y, z: {}, assignment)

