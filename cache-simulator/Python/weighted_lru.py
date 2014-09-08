import cache
import pprint
from sim import Sim
from collections import Counter
from operator import itemgetter


class Weighted_lru(Sim):

    def __init__(self, filename=None, blocksize=8, cachesize=80):
        Sim.__init__(self, filename=None, blocksize=8, cachesize=80)

    def sim_read(self, disk_id, block_address):
        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "hits"] += 1
        else:
            new_cache_block = cache.Cache()
            id_to_evict = self.find_id_to_evict(disk_id, block_address)
            if (len(self.ssd[disk_id]) >= self.weight[disk_id]):
                self.ssd[id_to_evict].popitem(last=False)
                self.stats[id_to_evict, "evictions"] += 1
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "misses"] += 1

    def calculate_size(self):
        count = {}
        for key, value in self.ssd.items():
            count[key] = len(value)
        return count

    def find_id_to_evict(self, disk_id, block_address):
        ssd_size = self.calculate_size()
        delta = Counter(ssd_size) - Counter(self.weight)
        try:
            id_to_be_evicted = max(delta.iteritems(), key=itemgetter(1))[0]
        except ValueError:
            # If all items are exactly equal to their weight,
            # delta would be an empty sequence, hence ValueError.
            return disk_id
        else:
            return id_to_be_evicted

    def print_stats(self):
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()
