import cache
import pprint
from sim import Sim
from operator import itemgetter
from collections import Counter


class Weighted_lru(Sim):

    def __init__(self, blocksize, cachesize):
        Sim.__init__(self, blocksize, cachesize)
        self.counter = Counter({1: 0, 2: 0, 3: 0, 4: 0})

    def sim_read(self, disk_id, block_address):
        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "hits"] += 1
        else:
            new_cache_block = cache.Cache()
            # If the given disk has no space
            if sum(self.counter.values()) == self.maxsize:
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

    def print_stats(self):
        pprint.pprint(dict(self.stats))
        # print self.ssd
