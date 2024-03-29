This program is a sequential Parda implementation on file input.

Instructions to run file input Parda.

#Setup

Step 0: parda use glib standard linux library. If on ubuntu system just execute following sudo command.

`sudo apt-get install glib-2.0`

#Compilation
Step 1: compile the program into .so file.

###Generic

`gcc -Wall -O2 `\`pkg-config --cflags --libs glib-2.0\``  -o parda.so -shared -fPIC splay.c parda.c parda_print.c narray.c -pthread -lgthread-2.0 -lglib-2.0`

OR

###For 32-bit arch:

`gcc -Wall  -O2 -I/usr/include/glib-2.0 -I/usr/lib/i386-linux-gnu/glib-2.0/include   -o parda.so -shared -fPIC splay.c parda.c parda_print.c narray.c -pthread -lgthread-2.0 -lglib-2.0`

###For 64-bit arch:

`gcc -Wall  -O2 -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include -o parda.so -shared -fPIC splay.c parda.c parda_print.c narray.c -pthread -lgthread-2.0 -lglib-2.0`

Step 2: Call the parda.so program in Python

the main function in parda.c is void classical_tree_based_stackdist(char* inputFileName, long lines)

--inputFileName: the input trace file name.

--lines: the total number of lines in the input trace file.

Reference: https://bitbucket.org/niuqingpeng/file_parda
