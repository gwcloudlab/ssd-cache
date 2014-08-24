'''
Cache simulator
'''

import os
import sys
import cache
import csv
import pprint

class Sim(object):
	
	def __init__(self, filename=None, blocksize=16, cachesize=64):
		self.ssd = {}  # This will be the actual cache
		self.filename 	= filename
		self.blocksize 	= blocksize
		self.cachesize 	= cachesize
		self.state = {
			"misses"	: 0,
			"hits"		: 0,
			"evictions"	: 0  
		}

		self.config = {
			"blocksize": blocksize,
			"cachesize": cachesize
		}

	def checkFreeSpace(self):
		if (len(self.ssd) < cachesize/blocksize):
			return True
		else:
			return False

	def sim_write(self, block_address, disk_id):
		pass

	def sim_read(self, block_address, disk_id):
		'''
		Check if the block is in the cache and update the stats
		for that object. If not call insert funtion and handle the miss
		'''
		if ((block_address, disk_id) in self.ssd):
			self.state["hits"] += 1
			self.ssd[block_address, disk_id].increment_lru()
			self.ssd[block_address, disk_id].increment_accesses()
		else:
			self.state["misses"] += 1
			self.insert(block_address, disk_id)

	def insert(self, block_address, disk_id):
		new_cache_block = cache.Cache()
  		if self.checkFreeSpace:
  			self.ssd[block_address, disk_id] = new_cache_block
  		else:
  			self.state["evictions"] += 1
  			lowest_lru = self.ssd[0][0] #Assign the first element's lru
  			index = 0
  			for key, cache_block in self.ssd.iteritems():
  				if cache_block.get_lru() < lowest_lru:
  					lowest_lru = cache_block.lru
  					indx = key
  			self.ssd[key] = new_cache_block
  			self.ssd[key].increment_lru()
  			self.ssd[block_address, disk_id].increment_accesses()


   	def delete(self):
   		self.resetCache()

   	def print_stats(self):
   		print self.config
   		print self.state
   		print self.ssd

  	# Zero out cache blocks/flags/values
  	def resetCache(self):
  		self.ssd.clear()

	def run(self):
		# Read a trace file
		try:
			with open(self.filename, "rb") as trace:
				for item in csv.reader(trace, delimiter=','):
					operation,block_address,disk_id = item[0], int(item[1], 0), int(item[2], 0)
					if operation == 'r':
						self.sim_read(block_address, disk_id)
					else:
						self.sim_write(block_address, disk_id)
			self.print_stats()
			return True
		except IOError as error:
			print("ERROR: Error loading trace: " +
                  err.filename + os.linesep +
                  " with error: " + err.message + os.linesep)
			return False
