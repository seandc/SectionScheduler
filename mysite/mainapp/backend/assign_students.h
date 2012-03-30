#ifndef ASSIGN_STUDENTS_H
#define ASSIGN_STUDENTS_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// A structure for storing a domain
struct domain{
    int size;
    int * values;
};

// A structure for storing the assignment
struct assignment{
    int total; // leaders + students
    int leaders; // The number of section leaders
    int students; // The number of student leaders
    int * genders; // A table giving the genders of the students;
    int * female_count; // A table the counts the number of women in each section
    struct domain * bin_constraints; // The binary constraints

    int * section_assignments; // The actual section assignents
    int times; // Number of potential section times
    int students_assigned;
    int leaders_assigned;
    int * has_leader; // Array of indicating which sections have leaders
    int * student_count; // The number of students in each section

    // Flags for different inconsistencies
    short section_has_more_than_one_leader;
    short too_few_students_in_a_section;
    short student_in_section_with_no_leader;
};

// Function prototypes for assignment.c
struct assignment * initialize_assignment(int total, int leaders, int times, int * genders, struct domain * bin_constraints);
void free_assignment(struct assignment * a);
void set_section(struct assignment * a, int key, int item);
int get_section(struct assignment * a, int key);
int equal_assignments(struct assignment * a, struct assignment * b);
void print_assignment(struct assignment * assignment);
struct assignment * deepcopy_assignment(struct assignment * original);

// Functions prototypes for backtracking.c
void zeros(int * a, int n);
double gender_cost(int section, struct assignment * a);
double cost(struct assignment * a);
int is_consistent(struct assignment * a, int var, int value);
int backtracking_search(struct assignment * a, struct domain * D, int * result, int max_seconds);

// Function prototypes for assign_students.c
int * assign_students(struct domain * D, int total, int leaders, int times, int * genders, struct domain * bin_constraints, int max_seconds);

#endif
