# The is a special list-like object that can be used for
# the cs 1 section assignment problem. It allows consistency
# to be checked in constant time for all non-complete assignments
# and in O(n) time for complete assignments where n is the number
# of possible times.

# Note that using this data structure for minconflicts will cause
# the minconflicts algorithm to fail.
class cs1_assignment(object):
    def __init__(self, total, leaders, times):
        self.leaders = leaders
        self.students = total - leaders
        n_over_k = float(self.students)/float(leaders)
        self.max_count = n_over_k + 1
        self.min_count = n_over_k - 1

        self.assignment = [None]*total
        self.students_assigned = 0
        self.leaders_assigned = 0
        self.has_leader = [0]*times
        self.student_count = [0]*times

        # These properties could probably be merged but 
        # this format is good for debugging.
        self.section_has_more_than_one_leader = False
        self.too_many_students_in_a_section = False
        self.too_few_students_in_a_section = False
        self.student_in_section_with_no_leader = False

    # Define the set item function so we can treat the data structure like 
    # a list. While assigning values it updates and checks a variety of 
    # properites of the object.
    def __setitem__(self, key, item):

        # If we are putting a non-None value into a None 
        # slot we need to decrement the assigment counts
        if self.assignment[key] == None and item != None:
            if key < self.leaders:
                self.leaders_assigned += 1
                self.has_leader[item] += 1
                if self.has_leader[item] > 1:
                    self.section_has_more_than_one_leader = True
            else:
                self.students_assigned += 1
                self.student_count[item] += 1
                count = self.student_count[item]

                # If all of the leaders have been assigned then we can rule out
                # any assignment of a student to a section with no leader. If the 
                # standard backtracking algorithm is used, all of the leaders will
                # always be assigned to before the students.
                if self.leaders_assigned == self.leaders and not self.has_leader[item]:
                    self.student_in_section_with_no_leader = True

                # Check if the count exceeds the maximum count or if it impossible
                # for count to ever exceed the minimum count.
                if count > self.max_count:
                    self.too_many_students_in_a_section = True
                elif count + self.students - self.students_assigned < self.min_count:
                    self.too_few_students_in_a_section = True


        # If we are putting a None into a non-None slot
        # we need to decrement the assigment counts
        elif self.assignment[key] != None and item == None:
            if key < self.leaders:
                # Decrement the number of leaders assigned
                self.leaders_assigned -= 1
                self.has_leader[self.assignment[key]] -= 1
                
                # Any illegal assigment will be immediately undone
                # so we can set this value to False unconditionally
                self.section_has_more_than_one_leader = False
            else:
                # Decrement the number of students assigned
                self.students_assigned -= 1
                self.student_count[self.assignment[key]] -= 1

                # Any illegal assignment will be immediately undone
                # so we can set these values to False unconditionally
                self.too_many_students_in_a_section = False
                self.too_few_students_in_a_section = False
                self.student_in_section_with_no_leader = False

        # This is the O(n) check that occurs on complete sections.  It checks to make sure that 
        # no sections have fewer then the minimum number of students.
        if self.students + self.leaders == self.students_assigned + self.leaders_assigned:
            if reduce(lambda accu, x : accu or (x and x < self.min_count), self.student_count, False):
                self.too_few_students_in_a_section = True

        # Assign the item
        self.assignment[key] = item

    # Get item and len just call the functions of the assignment list
    def __getitem__(self, key):
        return self.assignment[key]
    def __len__(self):
        return len(self.assignment) 
    def __repr__(self):
        return repr(self.assignment)


