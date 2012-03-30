from section_assignment import *
from random_data_generator import *
from ctypes import *

# The python equivalent of the C domain structure
class domain(Structure):
    _fields_ = [("size", c_int), ("values", POINTER(c_int))]

# Function that converts a single python domain to a c domain
def py_domain_to_c_domain(d):
    values = (c_int * len(d))(*list(d))
    size = len(d)
    return domain(size, values)

# Function that converts a python list of domains to a c pointer to domain
def py_domains_to_c_domains(ds):
    d_list = map(lambda d : py_domain_to_c_domain(d), ds)
    return (domain * len(d_list))(*d_list)

def list_from_pointer(p_int, n):
    ls = []
    for i in range(n):
        ls.append(p_int[i])
    return ls

# Load the shared C library and extract the needed function
libbt = CDLL("./libbt.so")
solver = libbt.assign_students
solver.restype = POINTER(c_int)

# Data should be a dictionary with student names as keys.
def assign_students(data, max_time):
    D, X, ints_to_domains, leader_count, gender_table, bin_constraints = generate_availability_problem(data)
    genders = (c_int * len(X))(*gender_table)
    c_D = py_domains_to_c_domains(D)
    c_bin_constrains = py_domains_to_c_domains(bin_constraints)
    c_result = solver(c_D, c_int(len(X)), c_int(leader_count), c_int(len(ints_to_domains)), genders, c_bin_constraints, max_time)
    result = list_from_pointer(c_result, len(X))
    student_to_section = {}
    for i in range(len(result)):
        student_to_section[X[i]] = ints_to_domains[result[i]] if result[i] >= 0 else "NO ASSIGNMENT"
    return student_to_section


