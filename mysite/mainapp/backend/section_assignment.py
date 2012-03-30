# Function that loads the student availability data from the given csv files and outputs a csp along 
# with information that 
def generate_availability_problem(data):

    leaders = []
    leader_domains = []
    students = []
    student_domains = []

    for name in data:
        student = data[name]
        availabilities = student['section_availability_ordered']

        # Check if they are a ta
        if student['is_ta'] == "true":
            leaders.append(name)
            leader_domains.append(set(availabilities))
        else:
            students.append(name)
            student_domains.append(set(availabilities))

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
        gender_table[i] = 0 if data[leaders[i]]['is_male'] == 'true' else 1 
    for i in range(student_count):
        X[i + leader_count] = students[i] 
        name_to_int[students[i]] = i + leader_count
        gender_table[i + leader_count] = 0 if data[students[i]]['is_male'] == 'true' else 1 

    # Initialize and empty list of binary constraints
    bin_constraints = [set() for i in len(X)]
    for name in data:
        for r in data[name]['cant_be_with']:
            if r in data:
                bin_constraints[name_to_int[r]].add(name_to_int[name])

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

    # Return the csp and the table for getting domain strings from integers
    return D, X, ints_to_domains, leader_count, gender_table, bin_constraints

# Pretty print the result of a 
def pretty_print_sections(D, X, assignment, ints_to_domains, section_leaders):

    # Initialize the section strings:
    section_strings = {}
    for i in range(section_leaders):
        section = assignment[i]
        section_strings[section] =  ['Time: ', ints_to_domains[section], 
                                     '\nLeader: ', X[i],
                                     '\nStudents:\n']

    # Add the students to their assigned sections
    for i in range(section_leaders, len(assignment)):
        section_strings[assignment[i]].append('\t' + X[i] + '\n')

    # Print the section strings
    for i in section_strings:
        print ''.join(section_strings[i])
