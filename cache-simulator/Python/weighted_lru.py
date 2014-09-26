from __future__ import division
from cache_entry import Cache_entry
import pprint
from cache import Cache
from operator import itemgetter
from collections import Counter, defaultdict, OrderedDict
from numpy import cumsum


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
            sz = len(self.rd[disk_id])
            self.rd[disk_id].pop(block_address)
            self.rd[disk_id][block_address] = sz - indx
        else:
            self.rd[disk_id][block_address] = 0

    def construct_rd_cdf(self):
        """
        The estimated hit ratio for each disk is calculated from it's RD by first
        constructing a list ("histogram") of all RD values for each disk, i.e., All the RD
        values (one value per block) is copied into a list. This list, for each disk,
        is then normalized by it's total and the list is sorted. Now, for each disk
        we have a normalized array of RD values. Then the cdf of each of the list is
        calculated by using the cumsum function from numpy library.
        """

        # calculate the normalized rd array
        rd_array_normalized = {}
        for disk, block in self.rd.iteritems():
            total = sum(block.itervalues())
            if total == 0:
                rd_array_normalized[disk] = [0]
            else:
                rd_array_normalized[disk] = sorted([value / total for value in block.itervalues()])

        # calculate the cdf of each disk
        cdf = {}
        for disk in rd_array_normalized.iterkeys():
            cdf[disk] = cumsum(rd_array_normalized[disk])


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
