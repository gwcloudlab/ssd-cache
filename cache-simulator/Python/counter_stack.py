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
import copy

class Counter_stack(object):

    def __init__(self, no_of_disks):
        self.counter_interval = 3  #sample interval for downsampling
        self.counter_step = 0  # current number for Counter Stack
        self.blocks_trace = defaultdict(lambda: [])
	self.counterStack_list = defaultdict(lambda: [])
	self.counterStack_prelist = defaultdict(lambda: [])

    def counter_stack_naive(self, disk_id, block_address, rd):
        """
        rd[disk] = ordereddict{ block_address : RD value }
        """
	reuse_distance= -1
	deltaX_list = [1]
	deltaY_list = [0]
	self.counterStack_prelist=copy.copy(self.counterStack_list[disk_id])
	self.counterStack_list[disk_id]=[]
	hyperll = hyperloglog.HyperLogLog(0.01)
        unique_blocks = {}
	unique_blocks = hyperll
	self.blocks_trace[disk_id].append(str(block_address))
	"""
	print "self.blocks_trace: "
	for x in self.blocks_trace[disk_id]:
	    print x
	"""
	# compute the Naive Counter Stack
	for x in range(0,len(self.blocks_trace[disk_id]))[::-1]:
	    unique_blocks.add(str(self.blocks_trace[disk_id][x]))
	    self.counterStack_list[disk_id].append(len(unique_blocks))
	
	# compute the delta X	deltaXij=Ci,j - Ci,j-1   
	for c in range(0,len(self.counterStack_prelist)):
	    deltaX=self.counterStack_list[disk_id][c+1]-self.counterStack_prelist[c]
	    deltaX_list.append(deltaX)
	""" if deltaX == 0:
		reuse_distance=self.counterStack_prelist[x]
		break
	"""
	# compute the delta Y	deltaYij=deltaXi+1,j - deltaXi,j
	if len(deltaX_list)>1:
	    for x in range(0,len(deltaX_list)-1):
		deltaY=deltaX_list[x]-deltaX_list[x+1]
		deltaY_list.append(deltaY)
		if deltaY == 1:
		    reuse_distance=self.counterStack_prelist[x]
		    break
	rd[disk_id][block_address]=reuse_distance
	file_name="stream.dat"
	self.save_counterStack_stream(file_name, disk_id)
	self.print_counterStack(disk_id)	
	print "reuse_distance: " + str(reuse_distance)
	return rd

    def save_counterStack_stream(self, file_name, disk_id):
	counterStack_strlist=[]
	for i in range(0, len(self.counterStack_list[disk_id])):
	    counterStack_strlist.append(str(self.counterStack_list[disk_id][i]))
	with open(os.path.join('traces', file_name), 'a') as counterStack_stream:
        # save Counter Stack stream
	    counterStack_stream.writelines(counterStack_strlist)
	    counterStack_stream.write("\n")

    def counter_stack_downsampling(self, disk_id, block_address, rd):
        self.counter_step += 1
        if self.counter_step % self.counter_interval ==0:
	   return self.counter_stack_naive(disk_id, block_address, rd)
	return rd

    def print_counterStack(self, disk_id):
	print "\nCounterStack: "
	print self.counterStack_list[disk_id]
	print "\n"

