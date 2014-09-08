#!/usr/bin/env python

'''
Main Function for cache for class
'''
import os
import csv
from global_lru import Global_lru
from static_lru import Static_lru
from weighted_lru import Weighted_lru


def main():
    world = Weighted_lru()
    filename = "sample.trace"

    try:
        with open(filename, "rb") as trace:
            for item in csv.reader(trace, delimiter=','):
                operation, block_address, disk_id = item[
                    0], int(item[1], 0), int(item[2], 0)
                world.sim_read(disk_id, block_address)
                # print world.ssd.keys()
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
