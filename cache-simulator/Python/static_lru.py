import cache
import pprint
from sim import Sim


class Static_lru(Sim):

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
            if (len(self.ssd[disk_id]) >= self.weight[disk_id]):
                self.ssd[disk_id].popitem(last=False)
                self.stats[disk_id, "evictions"] += 1
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "misses"] += 1

    def print_stats(self):
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()
