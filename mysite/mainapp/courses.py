# add new courses here
# users will be able to enter their schedule info at 
# this_site.com/enter_info/$course_id
# where $course_id is the key used for the course below
# raw availabilities (to be fed to a constraint satisfaction solver)
# this_site.com/raw_availabilities/$course_id
# they'll be in JSON
# and a viable assignment can be found at:
# this_site.com/assignment/$course_id
courses = {
    'CS111F': {
        "sections" : [
            "Monday 10pm to 11pm",
            "Tuesday 10pm to 11pm",
            "Wednesday 10pm to 11pm",
            ],
        "TAs" : [
            #'D. Parker Phinney',
            'Parker2'
            ],
        "students" : [
            "Alice",
            "Bob",
            "Charlie",
            ],
        }
}
