import cache
import pprint
from sim import Sim
from collections import OrderedDict


class Global_lru(Sim):

    def __init__(self, filename=None, blocksize=8, cachesize=80):
        Sim.__init__(self, filename=None, blocksize=8, cachesize=80)
        self.ssd = OrderedDict()

    def sim_read(self, disk_id, block_address):
        UUID = (disk_id, block_address)
        if (UUID in self.ssd):
            cache_contents = self.ssd.pop(UUID)
            self.ssd[UUID] = cache_contents
            self.ssd[UUID].set_lru()
            self.stats[UUID[0], "hits"] += 1
        else:
            new_cache_block = cache.Cache()
            if(len(self.ssd) >= self.maxsize):
                self.ssd.popitem(last=False)
                self.stats[UUID[0], "evictions"] += 1
            self.ssd[UUID] = new_cache_block
            self.stats[UUID[0], "misses"] += 1

    def print_stats(self):
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()