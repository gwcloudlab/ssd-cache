from __future__ import division
from cache_entry import Cache_entry
from statsmodels import api as sm
import os
from pprint import pprint
from cache import Cache
from operator import itemgetter
from collections import defaultdict, OrderedDict
from numpy import linspace
import hyperloglog
import time
from timeit import Timer
import random


class Rd_stack(Cache):

    def __init__(self, no_of_vms):
        Cache.__init__(self)
        # Number of cache items currently owned by each disk
        self.no_of_vms = no_of_vms
        self.rd = defaultdict(defaultdict)  # Reuse distance
        self.rd_blocks = defaultdict(list)
        self.rd_size = defaultdict(lambda: 0)

    def calculate_reuse_distance(self, disk_id, block_address):
        """
        For each block, the RD is calculated by the number of unique blocks
        accessed between two consecutive accesses of the block .
        The initial value of a new block is set to 0 and if that block is
        accessed again, it's index(position) in the list is obtained and
        it is moved to the end of the list. The value (new RD) of this block
        will be the number of blocks between it's index and it's current
        position (which is always at the end of the list).

        self.rd[disk] = ordereddict{ block_address : RD value }
        """
        if block_address in self.rd[disk_id]:
            indx = self.rd_blocks[disk_id].index(block_address)
            del self.rd_blocks[disk_id][indx]
            self.rd_blocks[disk_id].append(block_address)
            self.rd[disk_id][block_address] = self.rd_size[disk_id] - indx - 1
        else:
            self.rd_blocks[disk_id].append(block_address)
            self.rd[disk_id][block_address] = -1
            self.rd_size[disk_id] += 1
	return self.rd
