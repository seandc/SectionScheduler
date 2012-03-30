#include "assign_students.h"

struct assignment * initialize_assignment(int total, int leaders, int times, int * genders, struct domain * bin_constraints){
    struct assignment * a = (struct assignment *) malloc(sizeof(struct assignment));
    a->total = total;
    a->leaders = leaders;
    a->students = total - leaders;
    a->genders = genders;
    a->bin_constraints = bin_constraints;

    int i;
    int * female_count = (int *) malloc(times * sizeof(int));
    for (i = 0; i < times; i++){
        *(female_count + i) = 0;
    }
    a->female_count = female_count;
    a->times = times;

    // Initialize every assignment at -1
    int * section_assignments = (int *) malloc(total * sizeof(int));
    for (i = 0; i < total; i++){
        *(section_assignments + i) = -1;
    }
    a->section_assignments = section_assignments;

    a->students_assigned = 0;
    a->leaders_assigned = 0;

    // All of the sections start with no assigned leader
    int * has_leader = (int *) malloc(times * sizeof(int));
    for (i = 0; i < times; i++){
        *(has_leader + i) = 0;
    }
    a->has_leader = has_leader;

    // All of the sections start with no assigned students
    int * student_count = (int *) malloc(times * sizeof(int));
    for (i = 0; i < times; i++){
        *(student_count + i) = 0;
    }
    a->student_count = student_count;

    a->section_has_more_than_one_leader = 0;
    a->too_few_students_in_a_section = 0;
    a->student_in_section_with_no_leader = 0;

    return a;
}

void free_assignment(struct assignment * a){
    free(a->female_count);
    free(a->section_assignments);
    free(a->has_leader);
    free(a->student_count);
    free(a);
}

void set_section(struct assignment * a, int key, int item){
    if (*(a->section_assignments + key) < 0 && item >= 0){
        if (key < a->leaders){
            a->leaders_assigned += 1;
            *(a->has_leader + item) += 1;
            if (*(a->has_leader + item) > 1)
                a->section_has_more_than_one_leader = 1;
        }
        else{
            a->students_assigned += 1;
            *(a->student_count + item) += 1;
            int count = *(a->student_count + item);
            if (a->leaders_assigned == a->leaders && !*(a->has_leader + item))
                a->student_in_section_with_no_leader = 1;
        }
        int gender = *(a->genders + key);
        if (gender){
            *(a->female_count + item) += 1;
        }
    }

    else if (*(a->section_assignments + key) >= 0 && item < 0){
        if (key < a->leaders){
            a->leaders_assigned -= 1;
            *(a->has_leader + *(a->section_assignments + key)) -= 1;
            a->section_has_more_than_one_leader = 0;
        }
        else{
            a->students_assigned -= 1;
            *(a->student_count + *(a->section_assignments + key)) -= 1;

            a->too_few_students_in_a_section = 0;
            a->student_in_section_with_no_leader = 0;
        }
        int gender = *(a->genders + key);
        if (gender){
            *(a->female_count + *(a->section_assignments + key)) -= 1;
        }
    }

    if (a->students_assigned + a->leaders_assigned == a->total){
        int i;
        for (i = 0; i < a->times; i++){
            int count = *(a->student_count + i);
            if (!count && *(a->has_leader + i)){
                a->too_few_students_in_a_section = 1;
                break;
            }
        }
    }

    *(a->section_assignments + key) = item;
}

int get_section(struct assignment * a, int key){
    int * section_assignments = a->section_assignments;
    return *(section_assignments + key);
}

int equal_assignments(struct assignment * a, struct assignment * b){
    if (a->total != b->total){
        printf("Totals different\n");
        return 0;
    }
    if (a->leaders != b->leaders){
        printf("Leaders different\n");
        return 0;
    }
    if (a->students != b->students){
        printf("Students different\n");
        return 0;
    }
    if (memcmp(a->section_assignments, b->section_assignments, a->total * sizeof(int)) != 0){
        printf("Section assignments different\n");
        return 0;
    }
    if (a->times != b->times){
        printf("Times different\n");
        return 0;
    }
    if (a->students_assigned != b->students_assigned){
        printf("Students Assignend different\n");
        return 0;
    }
    if (a->leaders_assigned != b->leaders_assigned){
        printf("Leaders Assigned different\n");
        return 0;
    }
    if (memcmp(a->has_leader, b->has_leader, a->times * sizeof(int)) != 0){
        printf("Has Leader different\n");
        return 0;
    }
    if (memcmp(a->student_count, b->student_count, a->times * sizeof(int)) != 0){
        printf("Student Count different\n");
        return 0;
    }
    if (a->section_has_more_than_one_leader != b->section_has_more_than_one_leader){
        printf("section_has_more_than_one_leader different\n");
        return 0;
    }
    if (a->too_few_students_in_a_section != b->too_few_students_in_a_section){
        printf("too_few_students_in_a_section different\n");
        return 0;
    }
    if (a->student_in_section_with_no_leader != b->student_in_section_with_no_leader){
        printf("student_in_section_with_no_leader different\n");
        return 0;
    }
    return 1;
}

void print_assignment(struct assignment * assignment){
    int i;
    struct assignment a = *(assignment);
    printf("total: %d\n", a.total);
    printf("leaders: %d\n", a.leaders);
    printf("students: %d\n", a.students);
    printf("section_assignments: ");
    for (i = 0; i < a.total; i++){
        printf("%d ", *(a.section_assignments + i));
    }
    printf("\n");
    printf("times: %d\n", a.times);
    printf("students_assigned: %d\n", a.students_assigned);
    printf("leaders_assigned: %d\n", a.leaders_assigned);
    printf("has_leader: ");
    for (i = 0; i < a.times; i++){
        printf("%d ", *(a.has_leader + i));
    }
    printf("\n");
        printf("student_count: ");
    for (i = 0; i < a.times; i++){
        printf("%d ", *(a.student_count + i));
    }
    printf("\n");
    printf("section_has_more_than_one_leader: %d\n", a.section_has_more_than_one_leader);
    printf("too_few_students_in_a_section: %d\n", a.too_few_students_in_a_section);
    printf("student_in_section_with_no_leader: %d\n", a.student_in_section_with_no_leader);
}

struct assignment * deepcopy_assignment(struct assignment * original){
    // Make a new assignment struct an allocate space for it
    struct assignment * copy = (struct assignment *) malloc(sizeof(struct assignment));
    copy->total = original->total;
    copy->leaders = original->leaders;
    copy->students = original->students;
    copy->section_assignments = (int *) malloc(copy->total * sizeof(int));
    memcpy(copy->section_assignments, original->section_assignments, copy->total * sizeof(int));

    copy->times = original->times;
    copy->students_assigned = original->students_assigned;
    copy->leaders_assigned = original->leaders_assigned;
    copy->has_leader = (int *) malloc(copy->times * sizeof(int));
    memcpy(copy->has_leader, original->has_leader, copy->times * sizeof(int));
    copy->student_count = (int *) malloc(copy->times * sizeof(int));
    memcpy(copy->student_count, original->student_count, copy->times * sizeof(int));

    copy->section_has_more_than_one_leader = original->section_has_more_than_one_leader;
    copy->too_few_students_in_a_section = original->too_few_students_in_a_section;
    copy->student_in_section_with_no_leader = original->student_in_section_with_no_leader;
    return copy;
}
