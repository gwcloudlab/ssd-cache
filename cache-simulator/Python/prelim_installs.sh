#!/bin/bash

sudo apt-get install -y python-dev python-pip  python-setuptools python-numpy python-scipy python-flake8 libfreetype6-dev libxft-dev libpng-dev gcc-6 g++-6 glib-2.0

sudo pip install hyperloglog pandas numpy cython patsy statsmodels matplotlib mmh3

g++-6 sim_anneal.cpp -o sim_anneal

cd PARDA/
gcc -Wall -O2 `pkg-config --cflags --libs glib-2.0` -o parda.so -shared -fPIC splay.c parda.c parda_print.c narray.c -pthread -lgthread-2.0 -lglib-2.0
cd ../
ln -s PARDA/parda.so parda.so

mkdir -p log
touch sa_solution.txt
