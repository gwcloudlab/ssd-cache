#!/usr/bin/env python

'''
Main Function for cache for class
'''
import os
import csv
import math
from global_lru import Global_lru
from static_lru import Static_lru
from weighted_lru import Weighted_lru
from timeit import Timer
# import pdb


def run(world, filename):
    try:
        with open(os.path.join("traces/MSR-Cambridge/web", filename),
                  "rb") as trace:
            for item in csv.reader(trace, delimiter=','):
                time_of_access = int(item[0])
                # hostname = item[1]
                disk_id = int(item[2])
                operation = item[3]
                block_address = int(item[4])
                read_size = int(item[5])
                # response_time = int(item[6])
                blocks = int(math.ceil(read_size / 4096.0))
                if operation == "Read":
                    for block in xrange(blocks):
                        block_address += 1
                        world.sim_read(time_of_access, disk_id, block_address)
            # display_results(world.ssd)
            # pdb.set_trace()
        world.print_stats()
        return True
    except IOError as error:
        print("ERROR: Error loading trace: " +
              error.filename + os.linesep +
              " with error: " + error.message + os.linesep)
        return False


def display_results(ssd):
    for outer_key, outer_value in ssd.items():
        for inner_key in outer_value.keys():
            print outer_key, inner_key


def main():
    filename = "pre-processed_first_1000.csv"
    blocksize = 4096
    cachesize = 76684312576
    # There is a total of ~480K unique block addresses in the input file.
    # 196608000/4096 = 48K blocks (10% of total unique blocks)

    algorithms = [Global_lru, Static_lru, Weighted_lru]
    # algorithms = [Weighted_lru]
    for algorithm in algorithms:
        world = algorithm(blocksize, cachesize)
        t = Timer(lambda: run(world, filename))
        print "It took %s seconds to run" % (t.timeit(number=1))

if __name__ == '__main__':
    main()
