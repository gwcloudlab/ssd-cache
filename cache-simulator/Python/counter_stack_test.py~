from __future__ import division
from cache_entry import Cache_entry
from statsmodels import api as sm
import os
import pprint
from cache import Cache
from operator import itemgetter
from collections import Counter, defaultdict, OrderedDict
from numpy import linspace
import hyperloglog
import time
from timeit import Timer
import random
import csv
from counter_stack import Counter_stack

def main():
    filename = 'counter-stack-trace.csv'
    #filename = 'pre-processed_first_1000.csv'
    no_of_vms = 4
    rd = defaultdict(defaultdict)  # Reuse distance
    counterStack = Counter_stack(no_of_vms)
    try:
        with open(os.path.join('MSR', filename), "rb") as trace:
            lines_read = 0
            for item in csv.reader(trace, delimiter=','):
                lines_read += 1
                time_of_access = int(item[0])
                # hostname = item[1]
                disk_id = int(item[2])
                operation = item[3]
                block_address = int(item[4])
                read_size = int(item[5])
                # response_time = int(item[6])
                if operation == "Read":
		    #rd=counterStack.counter_stack_naive(disk_id, block_address,rd)
		    rd=counterStack.counter_stack_downsampling(disk_id, block_address,rd)
		    #print "lines_read: "+str(lines_read)
            print_reuse_distance(disk_id, rd)
            # pdb.set_trace()
    except IOError as error:
        print('ERROR: Error loading trace: ' +
              error.filename + os.linesep +
              " with error: " + error.message + os.linesep)

def print_reuse_distance(disk_id, rd):
    print "\nrd_begin"
    print rd
    print "rd_end\n"

if __name__ == '__main__':
    main()





