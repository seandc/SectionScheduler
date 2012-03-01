from backtracking import *
import csv
from collections import namedtuple
from random import random

# The single global constraint.  This is only recommended for use with
# minconflicts because it is much slower than fast_constraint below.
def global_constraint(times, min_count, max_count, leaders, assignment):

    students = len(assignment) - leaders

    has_section_leader = [False]*times # Keep track of which sections have a leader
    student_counts = [0]*times # Keep track of the number of students in each section
    total_assigned = 0 # Keep track of the total number of assigned students (including leaders)
    students_assigned = 0 # Keep track of the total number of non-leader students assigned

    # Go through each of the students (including section leaders)
    for person in range(len(assignment)):
        section = assignment[person]

        # Ignore people that haven't
        # been given assignments
        if section == None:
            continue
        total_assigned += 1

        # The section leaders were assigned the first
        # ids so we can check for membership using <
        if person < leaders:

            # Another leader was assigned to
            # this section so we return False
            if has_section_leader[section]:
                return False
            else:
                has_section_leader[section] = True

        else:
            student_counts[section] += 1
            students_assigned += 1

            # Figure out how many students were assigned to this section
            count = student_counts[section]

            # Make sure this assigmnent doesn't put the 
            # student count over the max
            if count > max_count:
                return False

            # Compute the number of non-leader students that have't been assigned
            remaining = students - students_assigned

            # There are not enough unassigned students to get this section up the min
            if count + remaining < min_count:
                return False

    # The following checks only occur for complete assignments
    if total_assigned == len(assignment):
        for section in range(times):

            # Get the number of students assigned to this time
            count = student_counts[section]

            # Only check sections with students in them
            if count:
                # Return False if there are students in a section with no section leader.
                if not has_section_leader[section]:
                    return False

                # Return False if there are fewer than the minimum required number of 
                # students in a section
                if count < min_count:
                    return False

    # If none of the tests failed return True
    return True

# This is a much faster constraint that takes advantage of the
# cs1_assignment class (see cs1_assignment.py). All of checking 
# is constant on non-complete assignments. Complete assignments
# require O(n) time where n is the total number of times to choose
# from.  Will not work with minconflicts.
def fast_constraint(a):
    if a.section_has_more_than_one_leader:
        # print 'Section has more than one leader'
        return False
    if a.too_many_students_in_a_section:
        # print 'Too many students in a section'
        return False
    if a.too_few_students_in_a_section:
        # print 'Too few students in a section'
        return False
    if a.student_in_section_with_no_leader:
        # print 'Students in section with no leader'
        return False
    return True

# Function to read student information from a csv file
def read_student_availability_data(path):
    students = []
    domains = []
    f = open(path, 'r')
    reader = csv.reader(f)
    for row in reader:
        name = row[0].strip()
        domain = set([row[i].strip() for i in range(1, len(row))])
        students.append(name)
        domains.append(domain)
    return students, domains

# Not equal binary constraint
def not_equal(x, y):
    return constraint((x, y), lambda a : a[x] == None or a[y] == None or a[x] != a[y])

# Ratio is the male to female ratio
def make_gender_constraint(times, min_count, gender_table):
    def f(a):
        if reduce(lambda accu, x : accu and (x != None), a, True):
            gender_counts = [[0,0] for i in range(times)]
            for i in range(len(a)):
                gender_counts[a[i]][gender_table[i]] += 1
            for men, women in gender_counts:
                if men or women:
                    if men == 0 or women == 0:
                        return True
                    elif (men < min_count or women < min_count):
                        return False
            return True
        else:
            return True
    return f

# Function that loads the student availability data from the given csv files and outputs a csp along 
# with information that 
def generate_availability_problem(data, use_fast_constraint = False):

    leaders = []
    leader_domains = []
    students = []
    student_domains = []

    for name in data:
        student = data[name]
        availabilities = student['section_availability_ordered']

        # Check if they are a ta
        if student['is_ta'] == 'True':
            leaders.append(name)
            leader_domains.append(set(availabilities))
        elif student['is_ta'] == 'False':
            students.append(name)
            student_domains.append(set(availabilities))
        else:
            raise ValueError('Invalid value for is_ta field')

    leader_count = len(leaders)
    student_count = len(students)
    
    # Make one list containing all of the sections for which leaders are available
    ints_to_domains = list(reduce(lambda a,b : a | b, leader_domains))

    # Make a dictionary from strings to integers
    domains_to_ints = {}
    for i in range(len(ints_to_domains)):
        domains_to_ints[ints_to_domains[i]] = i

    # and initalize the gender table as an empty list
    gender_table = [0]*(student_count + leader_count)

    # Assign numbers to the leaders and students
    # Leaders get the first numbers
    X = ['']*(leader_count + student_count)
    name_to_int = {}
    for i in range(leader_count):
        X[i] = leaders[i]
        name_to_int[leaders[i]] = i
        gender_table[i] = 0 if data[leaders[i]]['is_male'] == 'True' else 1 
    for i in range(student_count):
        X[i + leader_count] = students[i] 
        name_to_int[students[i]] = i + leader_count
        gender_table[i + leader_count] = 0 if data[students[i]]['is_male'] == 'True' else 1 

    # Initialize and empty list of binary constraints
    bin_constraints = []
    for name in data:
        for r in data[name]['cant_be_with']:
            bin_constraints.append(not_equal(name_to_int[name], name_to_int[r]))

    # Initialize the domain as empty sets
    D = [set() for i in range(leader_count + student_count)]

    # Make the domains for the leaders
    for i in range(leader_count):
        for x in leader_domains[i]:
            if x in domains_to_ints:
                D[i].add(domains_to_ints[x])

    # Make the domains for the students
    for i in range(student_count):
        for x in student_domains[i]:
            if x in domains_to_ints:
                D[i + leader_count].add(domains_to_ints[x])


    gender_constraint = make_gender_constraint(len(ints_to_domains), float(student_count)/float(leader_count) - 1.0, gender_table)

    # The number of students divided by the number of leaders
    n_over_k = float(student_count)/float(leader_count)

    # The definition of the constraint function depends on the use_fast_constraint flag. This is False by default. The fast
    # constraint should only be used with the 
    if use_fast_constraint:
        constraint_function = lambda a: fast_constraint(a) 
    else:
        constraint_function = lambda a : global_constraint(len(ints_to_domains), n_over_k - 1, n_over_k + 1, leader_count, a)

    # Make the csp
    csp = CSP(
        X,
        D,
        [constraint([i for i in range(student_count + leader_count)], constraint_function),
         constraint([i for i in range(student_count + leader_count)], gender_constraint)] + bin_constraints
    )

    # Return the csp and the table for getting domain strings from integers
    return csp, ints_to_domains, leader_count, gender_table

# Function to generate random availability lists.  
def generate_random_availability_lists(leader_names, student_names, leader_times, p, leader_path, student_path):

    # Make the leader availability list
    leader_rows = []
    student_times = set()
    for leader in leader_names:
        row = [leader]
        for time in leader_times:
            if random() < p:
                row.append(time)
                student_times.add(time) 
        leader_rows.append(row)

    # Now make the student availability list
    student_rows = []
    for student in student_names:
        row = [student]
        for time in student_times:
            if random() < p:
                row.append(time)
        student_rows.append(row)

    # Print the leader list to the csv file
    f = open(leader_path, 'w')
    writer = csv.writer(f)
    for row in leader_rows:
        writer.writerow(row)
    f.close()

    # Print the student list to the csv file
    f = open(student_path, 'w')
    writer = csv.writer(f)
    for row in student_rows:
        writer.writerow(row)
    f.close()

# Pretty print the result of a 
def pretty_print_sections(csp, assignment, ints_to_domains, section_leaders):

    # Initialize the section strings:
    section_strings = {}
    for i in range(section_leaders):
        section = assignment[i]
        section_strings[section] =  ['Time: ', ints_to_domains[section], 
                                     '\nLeader: ', csp.X[i],
                                     '\nStudents:\n']

    # Add the students to their assigned sections
    for i in range(section_leaders, len(assignment)):
        section_strings[assignment[i]].append('\t' + csp.X[i] + '\n')

    # Print the section strings
    for i in section_strings:
        print ''.join(section_strings[i])

# Generates the html code for the sections
def generate_section_html(csp, assignment, ints_to_domains, section_leaders):
    
    # Initialize the section strings:
    section_strings = {}
    for i in range(section_leaders):
        section = assignment[i]
        section_strings[section] =  ['<h3>' + ints_to_domains[section] + ' - ' + csp.X[i] + '</h3>',
                                     '<ul>']

    # Add the students to their assigned sections
    for i in range(section_leaders, len(assignment)):
        section_strings[assignment[i]].append('\t<li>' + csp.X[i] + '</li>')

    # Add the closing tag and a line break
    for i in section_strings:
        section_strings[i].append('</ul>')

    # Print the section strings
    html = []
    for i in section_strings:
        html.append('\n'.join(section_strings[i]))

    return '\n'.join(html)