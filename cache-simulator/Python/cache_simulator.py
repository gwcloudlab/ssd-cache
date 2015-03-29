#!/usr/bin/env python

'''
Main Function for cache for class
'''
import csv
import math
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


def run(world, filename, num_lines, no_of_vms):
    with open(filename, 'rb') as trace:
        one_percent_complete = round(num_lines / 100)
        lines_read = 0
        for item in csv.reader(trace, delimiter=','):
            lines_read += 1
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
                # print lines_read
            if(lines_read % one_percent_complete == 0):
                print 100 * lines_read / num_lines, " percent complete"
        # display_results(world.ssd)
        # pdb.set_trace()
    # world.print_stats()


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
    filename = 'MSR/tiny_hm.csv'
    num_lines, no_of_vms, vm_ids = pre_process_file(filename)
    metalog = {}
    metalog['Current Time'] = str(datetime.now())
    metalog['Input file'] = filename
    metalog['VM count'] = no_of_vms
    metalog['VM ids'] = vm_ids
    metalog['Input file line count'] = num_lines

    # algorithms = [Global_lru, Static_lru, Weighted_lru]
    # algorithms = [Multilevel_global_lru, Global_lru]
    algorithms = [Multilevel_weighted_lru]
    for algorithm in algorithms:
        # TODO (sunny) input vm ids instead of no_of_vms
        world = algorithm(no_of_vms)
        t = Timer(lambda: run(world, filename, num_lines, no_of_vms))
        metalog['Algorithm used'] = world.__class__.__name__
        metalog['Run Time'] = ('%.2f' % t.timeit(number=1))
        hrc_curve.print_stats(metalog, world.stats)
        # print "It took %s seconds to run" % (t.timeit(number=1))

if __name__ == '__main__':
    main()
