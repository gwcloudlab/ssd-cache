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
        self.blocks_trace = defaultdict(lambda: []) # block trace list
	self.counterStack_list = defaultdict(lambda: []) # current counter stack list
	self.counterStack_prelist = defaultdict(lambda: []) # previous counter stack list
	self.reuseDistance_list = defaultdict(lambda: []) # Reuse distance list
	self.rd_index = defaultdict(defaultdict)  # Reuse distance index dictionary
    def counter_stack_naive(self, disk_id, block_address):
        """
        rd_index[disk] = ordereddict{ block_address : RD index }
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

	# compute the delta Y	deltaYij=deltaXi+1,j - deltaXi,j
	if len(deltaX_list)>1:
	    for x in range(0,len(deltaX_list)-1):
		deltaY=deltaX_list[x]-deltaX_list[x+1]
		deltaY_list.append(deltaY)
		if deltaY == 1:
		    reuse_distance=self.counterStack_prelist[x]
		    break

	# save reuse distance to the reuse distance list
	if reuse_distance== -1:
	    self.rd_index[disk_id][block_address]=len(self.reuseDistance_list[disk_id])
	    self.reuseDistance_list[disk_id].append(reuse_distance)
	else:
	    index=self.rd_index[disk_id].get(block_address)
	    if index== None:
		reuse_distance= -1
		self.rd_index[disk_id][block_address]=len(self.reuseDistance_list[disk_id])
		self.reuseDistance_list[disk_id].append(reuse_distance)
	    else :
		self.reuseDistance_list[disk_id][index]=reuse_distance

	# save the Counter Stack stream to disc
	file_name="stream.dat"
	self.save_counterStack_stream(file_name, disk_id)
	return self.reuseDistance_list

    def counter_stack_simple(self, disk_id, block_address):
        """
        rd[disk] = ordereddict{ block_address : RD index }
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
	    if deltaX == 0:
		reuse_distance=self.counterStack_prelist[x]
		break

	# save reuse distance to the reuse distance list
	if reuse_distance== -1:
	    self.rd_index[disk_id][block_address]=len(self.reuseDistance_list[disk_id])
	    self.reuseDistance_list[disk_id].append(reuse_distance)
	else:
	    index=self.rd_index[disk_id].get(block_address)
	    if index== None:
		reuse_distance= -1
		self.rd_index[disk_id][block_address]=len(self.reuseDistance_list[disk_id])
		self.reuseDistance_list[disk_id].append(reuse_distance)
	    else :
		self.reuseDistance_list[disk_id][index]=reuse_distance
	return self.reuseDistance_list

    def save_counterStack_stream(self, file_name, disk_id):
	counterStack_strlist=[]
	for i in range(0, len(self.counterStack_list[disk_id])):
	    counterStack_strlist.append(str(self.counterStack_list[disk_id][i]))
	with open(os.path.join('traces', file_name), 'a') as counterStack_stream:
        # save Counter Stack stream
	    counterStack_stream.writelines(counterStack_strlist)
	    counterStack_stream.write("\n")

    def counter_stack_downsampling(self, disk_id, block_address):
        self.counter_step += 1
        if self.counter_step % self.counter_interval ==0:
	   return self.counter_stack_naive(disk_id, block_address)
	return self.reuseDistance_list
