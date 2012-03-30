#include "assign_students.h"
#include <math.h>
#include <float.h>
#include <time.h>

// Zero out an array, a, of length n.
void zeros(int * a, int n){
    int i;
    for (i = 0; i < n; i++){
        *(a + i) = 0;
    }
}

// The gender cost of a section is computed by squaring the 
// the absolute value of the difference between males and females.
// However if this value is less than or equal to 1 then a cost of 
// 0 is given.
double gender_cost(int section, struct assignment * a){
    int females = *(a->female_count + section);
    int males = *(a->student_count + section) - females;
    double diff = fabs(((double) males) - ((double) females));
    if (diff <= 1.0 || females == 0 || males == 0){
        return 0.0;
    }
    else{
        return pow(diff, 2.0);
    }
}

// The cost function is computed on complete assignments.
// It scores the assignments based on gender balance and
// balance of the number of students in each section.
double cost(struct assignment * a){
    int leaders = a->leaders;
    double total_gender_cost = 0.0;
    double error = 0.0;
    double mean = ((double) a->students) / ((double) a->leaders);

    // The section imbalance is the sum of the squared differences 
    // between the number of students in each section and the total
    // number of non-leaders students divided by the number of leaders. 
    // See gender_cost above for an explaination of how gender_cost
    // is determined.
    int i, count, section;
    for (i = 0; i < leaders; i++){
        section = *(a->section_assignments + i);
        count = *(a->student_count + section);
        error += pow((mean - count), 2.0);
        total_gender_cost += gender_cost(section, a);
    } 

    // The total cost is twice the section imbalance cost
    // plus the gender imbalance cost. The 2 is given to 
    // add greater signifigance to balancing the sizes.
    return 2*error + total_gender_cost;
}

// Make sure none of the binary constraints are violated. This code is O(n^2) where n 
// is the number of section leaders. The worst case is when the student cannot be with
// any section leader. However, most students will not have any restrictions in which 
// case this will take up no time. If they do have an issue it will probably only be 
// with a single TA. I do not think it is worthwhile to store additional information in the
// the assignment data structure or use a hashtable to improve the runtime.
int check_bin_constraints(struct assignment * a, int var, int val){
    if (var < a->leaders){
        return 1;
    }
    else{
        struct domain restrictions = *(a->bin_constraints + var);
        int i, j;
        for(i = 0; i < restrictions.size; i++){
            for(j = 0; j < a->leaders; j++){
                if ((*(a->section_assignments + j) == val) && (*(restrictions.values + i) == j))
                    return 0;
            }
        }
        return 1;
    }
}

// Checks if the assignment would be consistent if var took 
// on the given value from its domain.
int is_consistent(struct assignment * a, int var, int value){

    // Temporarily assign the variable
    set_section(a, var, value);

    // Check if the assignment generated any inconsistencies
    int status =  !(a->section_has_more_than_one_leader ||
                    a->too_few_students_in_a_section ||
                    a->student_in_section_with_no_leader);


    // Check the binary constraints
    status &= check_bin_constraints(a, var, value);

    // Unassign the variable
    set_section(a, var, -1);

    // Return 1 for consistent and false otherwise
    return status;
}

// This is a backtracking search that solves a constraint solving problem.  It seeks a consistent
// and complete solution that minimizes the cost function described above. After the algorithm has
// run for max_seconds, it will return the best solution found up to that point (If it found a solution).
// This implementation does not use any heuristics or inference techniques to speed up search.
int backtracking_search(struct assignment * a, struct domain * D, int * result, int max_seconds){
    time_t time_limit = time(NULL) + ((time_t)max_seconds);
    double upper_bound = DBL_MAX;
    int found_solution = 0;
    int n = a->total;
    int var, val, advance;

    // Make an array for tracking the positions in each domain
    int domain_pos[n];
    zeros(domain_pos, n);

    var = 0;
    while (0 <= var && var < n){
        advance = 0;

        /*
        int status = !(a->section_has_more_than_one_leader ||
                    a->too_few_students_in_a_section ||
                    a->student_in_section_with_no_leader);
        if (!status){
            printf("SOMETHING IS WRONG\n");
            print_assignment(a);
            exit(1);
        }
        */

        // Get the domain for this variable
        struct domain d = *(D + var);

        // While the domain is not empty
        while (*(domain_pos + var) < d.size){

            // Get the next value in the domain
            val = *(d.values + *(domain_pos + var));
            *(domain_pos + var) += 1;

            // Check if the the selected value would
            // make a consitent assignment.
            if (is_consistent(a, var, val)) {

                // Make the assignment and advance
                set_section(a, var, val);
                var++;

                // Restore the domain of the next variable
                *(domain_pos + var) = 0;
                advance = 1;
                break;
            }
        }

        // Backtrack
        if (!advance){
            var--;
	       if (var >= 0)
            	set_section(a, var, -1);
        }   
        // If the variable is greater then n then we have found a solution.
        else{
            if (var >= n){
                found_solution = 1;
                double c = cost(a);

                // Check if this assignment is an improvement over previously found
                // assignments and save it if it is.
                if (c < upper_bound){
                    upper_bound = c;
                    memcpy(result, a->section_assignments, n * sizeof(int));
                }

                // Continue searching for other assignments by backtracking.
                var--;
                set_section(a, var, -1);
            }
        }

        // Check if the algorithm has been running for 
        // longer than the specified time limit and break out 
        // of the while loop if time is up.
        if (time(NULL) > time_limit){
            printf("Reached Time Limit\n");
            break;
        }
    }

    // Inform the caller whether or not a solution was found. 1 for true 0 otherwise.
    return found_solution;
}
