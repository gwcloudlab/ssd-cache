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
from rd_stack import Rd_stack

def main():
    #filename = 'counter-stack-trace.csv'
    #filename = 'pre-processed.csv'
    filename = 'pre-processed_first_1000.csv'
    no_of_vms = 4
    num_lines = 3791
    counterStack = Counter_stack(no_of_vms)
    rdStack = Rd_stack(no_of_vms)
    try:
	time_begin=time.time()
	print "begin time: "+str(time_begin)	
	with open(os.path.join('MSR', filename), "rb") as trace:
	    one_percent_complete = round(num_lines / 1)
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
		    # print "lines_read: "+str(lines_read)+" block_address: "+str(block_address)
	    	    # reuseDistance=counterStack.counter_stack_naive(disk_id, block_address)
	    	    reuseDistance=counterStack.counter_stack_simple(disk_id, block_address)
		    #reuseDistance=rdStack.calculate_reuse_distance(disk_id, block_address)
        	#print_reuse_distance(disk_id, reuseDistance)
		if(lines_read % one_percent_complete == 0):
                    print 100 * lines_read / num_lines, " percent complete"

	time_end=time.time()
	print "end time: "+str(time_end)
	print "Total time: "+str(time_end-time_begin)
    except IOError as error:
        print('ERROR: Error loading trace: ' +
              error.filename + os.linesep +
              " with error: " + error.message + os.linesep)


def print_reuse_distance(disk_id, reuseDistance):
    print "\nrd_begin"
    print reuseDistance
    print "rd_end\n"

if __name__ == '__main__':
    main()





