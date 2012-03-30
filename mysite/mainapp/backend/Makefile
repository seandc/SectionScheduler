# Makefile for student assignment C library

library:
	gcc -c -O3 -fPIC assignment.c backtracking.c assign_students.h assign_students.c
	gcc -shared -o libbt.so assignment.o backtracking.o assign_students.o

debug: 
	gcc -g assignment.c backtracking.c assign_students.h assign_students.c main.c -o main

speed:
	gcc -03 assignment.c backtracking.c assign_students.h assign_students.c main.c -o main

clean: 
	rm assignment.o
	rm assign_students.h.gch
	rm assign_students.o
	rm backtracking.o
	rm libbt.so
