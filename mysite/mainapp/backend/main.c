#include "assign_students.h"
#include <time.h>

void swap(int i, int j, int * a){
    int temp = *(a + i);
    *(a + i) = *(a + j);
    *(a + j) = temp;
}

void shuffle(int * a, int n){
    int i, j;
    for (i = n - 1; i > 0; i--){
        j = rand() % i;
        swap(i, j, a);
    }
}

struct domain * generate_random_domain(int n, int times){
    int sections[times];
    int i;
    for (i = 0; i < times; i++){
        sections[i] = i;
    }
    struct domain * D = (struct domain *) malloc(n * sizeof(struct domain));
    int j;
    int lb = times / 2;
    for (i = 0; i < n; i++){
        int size = lb + (rand() % (times - lb));
        D->size = size;
        D->values = (int *) malloc(size * sizeof(int));
        shuffle(sections, times);
        memcpy(D->values, sections, size * sizeof(int));
        D++;
    }
    D -= n;
    return D;
}

struct domain * generate_trivial_domain2(int n, int leaders, int times){
    int sections[times];
    int i;
    for (i = 0; i < times; i++){
        sections[i] = i;
    }
    struct domain * D = (struct domain *) malloc(n * sizeof(struct domain));
    int j;
    int lb = times / 2;
    for (i = 0; i < n; i++){
        if (i < leaders){
            D->size = times;
            D->values = (int *) malloc(times * sizeof(int));
            memcpy(D->values, sections, times * sizeof(int));
        }
        else{
            int size = lb + (rand() % (times - lb));
            D->size = size;
            D->values = (int *) malloc(size * sizeof(int));
            shuffle(sections, times);
            memcpy(D->values, sections, size * sizeof(int));
        }
        D++;
    }
    D -= n;
    return D;
}

struct domain * generate_random_restrictions(int n, int leaders){
    struct domain * R = (struct domain *) malloc(n * sizeof(struct domain));
    int i, j;
    for (i = 0; i < n; i++){
        if (i < leaders){
            R->size = 0;
            R->values = (int *) malloc(0);
        }
        else{
            int size = (rand() % 2) & (rand() % 2) & (rand() % 2);
            R->size = size;
            R->values = (int *) malloc(size * sizeof(int));
            if(size){
                *(R->values) = rand() % leaders;
            }
        }
        R++;
    }
    R -= n;
    return R;
}

struct domain * no_restrictions(int n){
    int i;
    struct domain * R = (struct domain *) malloc(n * sizeof(struct domain));
    for (i = 0; i < n; i++){
        R->size = 0;
        R->values = (int *) malloc(0);
        R++;
    }
    R -= n;
    return R;
}

struct domain * make_trivial_domain(int n, int times){
    int sections[times];
    int i;
    for (i = 0; i < times; i++){
        sections[i] = i;
    }
    struct domain * D = (struct domain *) malloc(n * sizeof(struct domain));
    int j;
    for (i = 0; i < n; i++){
        D->size = times;
        D->values = (int *) malloc(times * sizeof(int));
        memcpy(D->values, sections, times * sizeof(int));
        D++;
    }
    D -= n;
    return D;
}

struct domain * make_trivial_domain3(int n, int leaders, int times){
    struct domain * D = (struct domain *) malloc(n * sizeof(struct domain));
    int i;
    for (i = 0; i < leaders; i++){
        (D + i)->size = 1;
        (D + i)->values = (int *) malloc(sizeof(int));
        *((D + i)->values) = i;
    }
    for (i = leaders; i < n; i++){
        (D + i)->size = 1;
        (D + i)->values = (int *) malloc(sizeof(int));
        *((D + i)->values) = rand() % leaders;
    }
    return D;
}

int * generate_random_genders(int n){
    int * genders = (int *) malloc(n * sizeof(int));
    int i;
    for (i = 0; i < n; i++){
        *(genders + i) = rand() % 2;
    }
    return genders;
}

void free_domain_ptr(struct domain * D, int n){
    int i;
    for (i = 0; i < n; i++){
        free(D->values);
        D++;
    }
    D -= n;
    free(D);
}

void print_domains(struct domain * D, int n){
    int i, j;
    for (i = 0; i < n; i++){
        printf("Var %d: ", i);
        for(j = 0; j < D->size; j++){
            printf("%d ", *(D->values + j));
        }
        printf("\n");
        D++;
    }
}

void pretty_print_result(int * a, int total, int leaders, int * genders){
    int i, j, section;
    for (i = 0; i < leaders; i++){
        section = *(a + i);
        printf("Leader %d (%d)\n", i, *(genders + i));
        printf("Time %d\n", section);
        for (j = leaders; j < total; j++){
            if (*(a + j) == section){
                printf("\t%d (%d)\n", j, *(genders + j));
            }
        }
        printf("\n");
    }
}

int main(int argc, char * argv[]){
    if(argc != 5){
        printf("usage: $ ./testing [Total # of students (including leaders)] [# of section leaders] [# of possible times] [max time in seconds]\n");
        exit(1);
    }
    srand(time(NULL)); 
    int total = atoi(argv[1]);
    int leaders = atoi(argv[2]);
    int times = atoi(argv[3]);
    int max_time = atoi(argv[4]);
    //struct domain * D = generate_random_domain(10, 6);
    struct domain * D = generate_random_domain(total, times);
    //struct domain * D = make_trivial_domain3(total, leaders, times);
    int * genders = generate_random_genders(total);
    struct domain * restrictions = generate_random_restrictions(total, leaders);
    //struct domain * restrictions = no_restrictions(total);
    printf("Domains:\n");
    print_domains(D, total);
    printf("Restrictions:\n");
    print_domains(restrictions, total);
    int * a = assign_students(D, total, leaders, times, genders, restrictions, max_time);
    int i;
    printf("Results:\n");
    for (i = 0; i < total; i++){
        printf("%d ", *(a + i));
    }
    printf("\n");
    pretty_print_result(a, total, leaders, genders);

    // Clean up
    free_domain_ptr(D, total);
    free_domain_ptr(restrictions, total);
    free(genders);
    free(a);

}
