from __future__ import division
from cache_entry import Cache_entry
import pprint
from cache import Cache
from operator import itemgetter
from collections import Counter, defaultdict
from time import time


class Weighted_lru(Cache):

    def __init__(self, blocksize, cachesize):
        Cache.__init__(self, blocksize, cachesize)
        # Number of cache items currently owned by each disk
        self.counter = Counter({1: 0, 2: 0, 3: 0})
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = defaultdict(set)
        self.ri = defaultdict()  # Reuse intensity
        self.time_interval = 20   # t_w from vCacheShare paper
        self.timeout = time() + self.time_interval

    def sim_read(self, disk_id, block_address):
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(block_address)
        if time() > self.timeout:
            self.timeout = time() + self.time_interval
            self.calculate_reuse_intensity()
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
        # print "Counter: ", self.counter
        # print "weight: ", self.weight
        delta = self.counter - self.weight
        # print "Delta: ", delta
        try:
            id_to_be_evicted = max(delta.iteritems(), key=itemgetter(1))[0]
        except ValueError:
            # If all items are exactly equal to their weight,
            # delta would be an empty sequence, hence ValueError.
            id_to_be_evicted = disk_id
        # print "ID to be evicted", id_to_be_evicted
        return id_to_be_evicted

    def calculate_reuse_intensity(self):
        for disk in xrange(self.no_of_vms):
            if len(self.unique_blocks[disk]) == 0:
                continue
            self.ri[disk] = (self.total_accesses[disk]
                             / (len(self.unique_blocks[disk])
                                * self.time_interval))
            # print "total_accesses of ", disk, ": ", self.total_accesses[disk]
            # print "uniq_blcks of ", disk, ": ", len(self.unique_blocks[disk])
            print "RI of ", disk, ": ", self.ri[disk]
        self.total_accesses.clear()
        self.unique_blocks.clear()

    def print_stats(self):
        print "\nWeighted LRU:\n"
        print "Weight: ", self.weight, "\n"
        pprint.pprint(dict(self.stats))
        # print self.ssd
