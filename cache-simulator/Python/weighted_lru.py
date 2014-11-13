from __future__ import division
from cache_entry import Cache_entry
from statsmodels import api as sm
import sys
import os
import pprint
from cache import Cache
from operator import itemgetter
from collections import Counter, defaultdict, OrderedDict
from numpy import linspace, array


class Weighted_lru(Cache):
    def __init__(self, blocksize, cachesize):
        Cache.__init__(self, blocksize, cachesize)
        # Number of cache items currently owned by each disk
        self.counter = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = defaultdict(set)
        self.rd = defaultdict(OrderedDict)  # Reuse distance
        self.ri = defaultdict()  # Reuse intensity
        self.time_interval = 100  # t_w from vCacheShare
        self.timeout = 0  # Sentinel

    def sim_read(self, time_of_access, disk_id, block_address):
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(block_address)
        self.calculate_reuse_distance(disk_id, block_address)
        if time_of_access > self.timeout:
            self.timeout = time_of_access + self.time_interval
            self.calculate_reuse_intensity()
            self.calculate_weight()  # Calculate weight according to the RI
            self.construct_rd_cdf()
        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "hits"] += 1
        else:
            new_cache_block = Cache_entry()
            # If the given disk has no space
            if sum(self.counter.values()) >= self.maxsize:
                id_to_evict = self.find_id_to_evict(disk_id, block_address)
                self.ssd[id_to_evict].popitem(last=False)
                self.counter[id_to_evict] -= 1
                self.stats[id_to_evict, "evictions"] += 1
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.counter[disk_id] += 1
            self.stats[disk_id, "misses"] += 1

    def find_id_to_evict(self, disk_id, block_address):
        delta = Counter(self.counter) - Counter(self.weight)
        try:
            id_to_be_evicted = max(delta.iteritems(), key=itemgetter(1))[0]
        except ValueError:
            # If all items are exactly equal to their weight,
            # delta would be an empty sequence, hence ValueError.
            id_to_be_evicted = disk_id
        return id_to_be_evicted

    def calculate_reuse_intensity(self):
        """
        Reuse Intensity = S_{total} / (t_w * S_unique)
        self.ri[disk] = float value
        """
        for disk in xrange(self.no_of_vms):
            if len(self.unique_blocks[disk]) == 0:
                # If S_unique is 0, then the priority is set to 0
                self.ri[disk] = 0
            else:
                self.ri[disk] = (self.total_accesses[disk]
                                 / (len(self.unique_blocks[disk])
                                    * self.time_interval))
        self.total_accesses.clear()
        self.unique_blocks.clear()

    def calculate_reuse_distance(self, disk_id, block_address):
        """
        For each block, the RD is calculated by the number of unique blocks
        accessed between two consecutive accesses of the block .
        The initial value of a new block is set to 0 and if that block is accessed
        again, it's index(position) in the list is obtained and it is moved to the
        end of the list. The value (new RD) of this block will be the number of blocks
        between it's index and it's current position (which is always at the end of the
        list).
        self.rd[disk] = ordereddict{ block_address : RD value }
        """
        if block_address in self.rd[disk_id]:
            indx = self.rd[disk_id].keys().index(block_address)
            self.rd[disk_id].pop(block_address)
            sz = len(self.rd[disk_id])
            self.rd[disk_id][block_address] = sz - indx
        else:
            self.rd[disk_id][block_address] = 0

    def construct_rd_cdf(self):
        """
        The estimated hit ratio for each disk is calculated from it's RD by first
        constructing a list ("histogram") of all RD values for each disk, i.e., All the RD
        values (one value per block) is copied into a list. The cdf of each of the list is
        calculated by using the sm.distributions.ECDF library function.
        """

        # calculate the normalized rd array
        rd_array = {}
        cdf_x = {}  # The x axis of the cdf
        cdf_y = {}  # The y axis of the cdf. i.e. the hit ratio
        min_rd_value = 0.0 # initialize min and max rd values. This is the x-axis values
        max_rd_value = 200.0
        with open(os.path.join('traces', 'wlru.dat'), 'w') as out_file:
            out_file.write(" " + str(4) + " " + str(50) + " " + str(1) + "\n")
            out_file.write(" " + str(150) + "\n")

            for disk, block in self.rd.iteritems():
                if sum(block.itervalues()) == 0:
                    cdf_x[disk] = 0
                    cdf_y[disk] = array([0])
                    out_file.write(" " + str(disk+1) + "\n")
                    for i in xrange(0, 50):
                        out_file.write(" " + str(0) + " " + str(0) + "\n")
                else:
                    rd_array[disk] = sorted(block.itervalues())
                    ecdf = sm.distributions.ECDF(rd_array[disk])
                    # cdf_x[disk] = linspace(min(rd_array[disk]), max(rd_array[disk])) # For continuous x values
                    # cdf_x[disk] = rd_array[disk]
                    cdf_x[disk] = linspace(min_rd_value, max_rd_value, 50) # 50 x tics
                    cdf_y[disk] = ecdf(cdf_x[disk])

                    out_file.write(" " + str(disk+1) + "\n")
                    for x_axis_value, y_axis_value in zip(cdf_x[disk], cdf_y[disk]):
                        out_file.write(" " + str('%.2f' % y_axis_value) + " " + str('%.2f' % x_axis_value) + "\n")
        os.system('/Users/sunny/Documents/ssd-cache/cache-simulator/Python/sim_anneal')
        # print "CDF(x)", cdf_x
        # print "CDF(y)", cdf_y



    def calculate_weight(self):
        """
            Calculate the weight of each VM/Disk based on their Priorities.
            The Priorities are calculated from their reuse intensity values.
            priority[disk] = ri / sum of ri's for all disks - normalized by sum.
            weight[disk] = priority * max size of the cache.
            For now, there is no upper bound.

            TO-DO: Calculate priorities using RD as well.
            """
        self.priority = {k: v / sum(self.ri.values())
                         for k, v in self.ri.items()}
        self.weight = {k: int(v * self.maxsize)
                       for k, v in self.priority.items()}

    def print_stats(self):
        print "\nWeighted LRU:\n"
        print "Weight: ", self.weight, "\n"
        pprint.pprint(dict(self.stats))
