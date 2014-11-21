from cache_entry import Cache_entry
import pprint
from cache import Cache


class Static_lru(Cache):

    def __init__(self):
        Cache.__init__(self)

    def sim_read(self, time_of_access, disk_id, block_address):
        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "hits"] += 1
        else:
            new_cache_block = Cache_entry()
            if (len(self.ssd[disk_id]) >= self.weight[disk_id]):
                self.ssd[disk_id].popitem(last=False)
                self.stats[disk_id, "evictions"] += 1
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "misses"] += 1

    def print_stats(self):
        print "\nStatic LRU:\n"
        print "Weight: ", self.weight, "\n"
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()
