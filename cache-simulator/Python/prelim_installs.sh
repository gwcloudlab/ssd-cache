#!/bin/bash

sudo apt-get install -y python-dev python-pip  python-setuptools python-numpy python-scipy python-flake8 libfreetype6-dev libxft-dev libpng-dev gcc-4.9 g++-4.9
sudo pip install hyperloglog pandas numpy cython patsy statsmodels matplotlib mmh3                                                                             

g++-4.9 sim_anneal.cpp -o sim_anneal

mkdir -p log
touch sa_solution.txt
