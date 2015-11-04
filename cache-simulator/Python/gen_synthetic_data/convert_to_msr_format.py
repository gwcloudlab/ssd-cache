from random import randint
import csv

with open("zipf.dat", 'r') as infile:
    zipf = infile.readlines()
counter = 0
time = 0
with open("synthetic_zipf.csv", 'w') as outfile:
    a = csv.writer(outfile, delimiter=',')
    for block in zipf:
        counter += 1
        if counter % 2 == 0:
            time += randint(0, 5)
        data = [time, "zipf", 0, "Read", int(block), 4096, 1]
        a.writerow(data)
