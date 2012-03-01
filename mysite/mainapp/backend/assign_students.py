from cs1_assignment import *
from section_assignment import *
from random_data_generator import *

# Data should be a dictionary with student names as keys.
def assign_students(data):
    csp, ints_to_domains, leader_count, gender_table = generate_availability_problem(data, True)
    result = (standard_bt_with_cs1_data(csp, leader_count, len(ints_to_domains))).assignment
    student_to_section = {}
    for i in range(len(result)):
        student_to_section[csp.X[i]] = ints_to_domains[result[i]]
    return student_to_section

#test_data = make_random_student_table(.5, .8, 4, 20)
#result = assign_students(test_data)

