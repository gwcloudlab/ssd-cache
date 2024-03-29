from cache_entry import Cache_entry
from collections import OrderedDict
from random import randint
from cache import Cache
import pprint


class Random_lru(Cache):

    def __init__(self, blocksize, cachesize):
        Cache.__init__(self, blocksize, cachesize)
        self.ssd = OrderedDict()

    def sim_read(self, time_of_access, disk_id, block_address):
        UUID = (disk_id, block_address)
        if (UUID in self.ssd):
            cache_contents = self.ssd.pop(UUID)
            self.ssd[UUID] = cache_contents
            self.ssd[UUID].set_lru()
            self.stats[UUID[0], "hits"] += 1
        else:
            new_cache_block = Cache_entry()
            if(len(self.ssd) >= self.maxsize):
                item_to_evict = randint(0, self.maxsize)
                del self.ssd[item_to_evict]
                self.stats[UUID[0], "evictions"] += 1
            self.ssd[UUID] = new_cache_block
            self.stats[UUID[0], "misses"] += 1

    def print_stats(self):
        print "\nGlobal LRU:\n"
        print "Maxsize: ", self.maxsize, "\n"
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()
