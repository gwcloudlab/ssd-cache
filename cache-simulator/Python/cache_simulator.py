#!/usr/bin/env python

'''
Main Function for cache for class
'''
import csv
import math
import sys
import os
# from global_lru import Global_lru
# from random_lru import Random_lru
# from static_lru import Static_lru
# from weighted_lru import Weighted_lru
# from multilevel_global_lru import Multilevel_global_lru
from multilevel_weighted_lru import Multilevel_weighted_lru
from timeit import Timer
from datetime import datetime
import hrc_curve
# import pdb


def run(world, filename):
    file_size = os.stat(filename).st_size
    with open(filename, 'rb') as trace:
        bytes_read = 0
        for item in csv.reader(trace, delimiter=','):

            bytes_read += 37  # 37 bytes per line, hardcoded
            percent = bytes_read*100 / file_size
            sys.stdout.write('\r Percentage: ' + str(percent) + '%')
            sys.stdout.flush()

            time_of_access = int(item[0])
            # hostname = item[1]
            disk_id = int(item[2])
            # operation = item[3]
            block_address = int(item[4])
            read_size = int(item[5])
            # response_time = int(item[6])
            blocks = int(math.ceil(read_size / 4096.0))
            for block in xrange(blocks):
                if block > 0:
                    block_address += 1
                world.sim_read(time_of_access, disk_id, block_address)
        # pdb.set_trace()


def pre_process_file(filename):
    """
     calculate the number of lines and the
     number of VMs in the input file.
    """

    num_lines = 0
    vm_ids = set()
    with open(filename) as trace:
        for item in csv.reader(trace, delimiter=','):
            num_lines += 1
            disk_id = int(item[2])
            vm_ids.add(disk_id)   # can make it more efficient
    no_of_vms = len(vm_ids)
    return (num_lines, no_of_vms, vm_ids)


def display_results(ssd):
    for outer_key, outer_value in ssd.items():
        for inner_key in outer_value.keys():
            print outer_key, inner_key


def main():
    filename = 'MSR/hm.csv'
    num_lines, no_of_vms, vm_ids = pre_process_file(filename)
    metalog = {}
    metalog['Current Time'] = str(datetime.now())
    metalog['Input file'] = filename
    metalog['VM count'] = no_of_vms
    metalog['VM ids'] = vm_ids
    metalog['file_size'] = os.stat(filename).st_size

    # algorithms = [Global_lru, Static_lru, Weighted_lru]
    # algorithms = [Multilevel_global_lru, Global_lru]
    algorithms = [Multilevel_weighted_lru]
    for algorithm in algorithms:
        # TODO (sunny) input vm ids instead of no_of_vms
        world = algorithm(vm_ids)
        t = Timer(lambda: run(world, filename))
        metalog['Algorithm used'] = world.__class__.__name__
        metalog['Run Time'] = ('%.2f' % t.timeit(number=1))
        hrc_curve.print_stats(metalog, world.stats)
        # print "It took %s seconds to run" % (t.timeit(number=1))

if __name__ == '__main__':
    main()
