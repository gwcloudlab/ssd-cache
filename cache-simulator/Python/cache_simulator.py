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
                time_of_access, hostname, disk_id, operation, \
                    block_address, read_size, response_time = \
                    int(item[0]), item[1], int(item[2]), item[3], \
                    int(item[4]), int(item[5]), int(item[6])
                # print "input: ", disk_id, block_address
                world.sim_read(disk_id, block_address)
                blocks = int(math.ceil(read_size / 4096.0))
                for block in xrange(blocks):
                    block_address += 1
                    world.sim_read(disk_id, block_address)
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
    filename = "web_traces.csv"
    blocksize = 4096
    cachesize = 19660800000
    # There is a total of ~480K unique block addresses in the input file.
    # 196608000/4096 = 48K blocks (10% of total unique blocks)

    #algorithms = [Global_lru, Static_lru, Weighted_lru]
    algorithms = [Global_lru]
    for algorithm in algorithms:
        world = algorithm(blocksize, cachesize)
        t = Timer(lambda: run(world, filename))
        print "It took %s seconds to run" % (t.timeit(number=1))

if __name__ == '__main__':
    main()
