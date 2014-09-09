#!/usr/bin/env python

'''
Main Function for cache for class
'''
import os
import csv
from global_lru import Global_lru
from static_lru import Static_lru
from weighted_lru import Weighted_lru
# import pdb


def display_results(ssd):
    for outer_key, outer_value in ssd.items():
        for inner_key in outer_value.keys():
            print outer_key, inner_key


def main():
    world = Weighted_lru(blocksize=4096, cachesize=196608000)
    # There is a total of ~480K unique block addresses in the input file.
    # 196608000/4096 = 48K blocks (10% of total unique blocks)
    filename = "WebSearch1.csv"
    try:
        with open(filename, "rb") as trace:
            for item in csv.reader(trace, delimiter=','):
                disk_id, block_address, read_size, operation, time_of_access \
                    = int(item[0]), int(item[1]), int(item[2], 0), item[
                        3], float(item[4])
                # print "input: ", disk_id, block_address
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

if __name__ == '__main__':
    main()
