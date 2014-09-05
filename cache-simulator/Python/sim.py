'''
Cache simulator
'''

from collections import defaultdict, OrderedDict, Counter
from operator import itemgetter
import pprint
import os
import csv
import cache
# import pdb


class Sim(object):

    def __init__(self, filename=None, blocksize=8, cachesize=80):
        self.EVICT_POLICY = "staticLRU"
        # This will be the actual cache
        self.ssd = defaultdict(lambda: OrderedDict())
        self.filename = filename
        self.blocksize = blocksize
        self.cachesize = cachesize
        # max size and self.weight's sum should be equal
        self.maxsize = cachesize / blocksize
        # Assign priority on the scale of 1 to 10
        self.priority = {1: 4, 2: 3, 3: 2, 4: 1}
        self.weight = {k: int(v * self.maxsize / 10)
                       for k, v in self.priority.items()}
        self.counter = {}
        self.stats = defaultdict(lambda: 0)
        self.config = {
            "blocksize": blocksize,
            "cachesize": cachesize
        }
        self.state = {
            "misses"	: 0,
            "hits"		: 0,
            "evictions"	: 0
        }

    def checkFreeSpace(self, disk_id):
        if (len(self.ssd[disk_id]) < self.weight[disk_id]):
            if self.EVICT_POLICY == "staticLRU":
                return len(self.ssd[disk_id]) < self.weight[disk_id]
            else:  # Both global and weighted LRU care only about maxsize
                return True
        return False

    def sim_read(self, disk_id, block_address):
        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.state["hits"] += 1
            self.stats[disk_id, "hits"] += 1
        else:
            self.insert(disk_id, block_address)
            self.state["misses"] += 1
            self.stats[disk_id, "misses"] += 1

    def insert(self, disk_id, block_address):
        new_cache_block = cache.Cache()
        if self.checkFreeSpace(disk_id):
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
        else:
            self.evictItem(disk_id, block_address)
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.state["evictions"] += 1
            self.stats[disk_id, "evictions"] += 1

    def evictItem(self, disk_id, block_address):
        if self.EVICT_POLICY == "weightedLRU":
            delta = Counter(
                self.ssd[block_address].counter) - Counter(self.weight)
            # Negative values are ignored in the above expression.
            # We don't need them. To not ignore use:
            # delta = k: self.ssd[block_address].counter.get(k
            # , 0) - self.weight.get(k, 0) for k in set(self.ssd[
            # block_address].counter) & set(self.weight) }
            try:
                id_to_be_evicted = max(delta.iteritems(), key=itemgetter(1))[0]
            except ValueError:
                # If all items are exactly equal to their weight,
                # delta would be an empty sequence, hence ValueError.
                self.ssd[disk_id].popitem(last=False)
            else:
                self.ssd[id_to_be_evicted].popitem(last=False)
        elif self.EVICT_POLICY == "staticLRU":
            self.ssd[disk_id].popitem(last=False)
        else:
                # TO-DO: Code for global LRU condition
            pass

    def delete(self):
        self.resetCache()

    def print_stats(self):
        # print self.config
        pprint.pprint(self.state)
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()

    # Zero out cache blocks/flags/values
    def resetCache(self):
        self.ssd.clear()

    def run(self):
        # Read a trace file
        try:
            with open(self.filename, "rb") as trace:
                for item in csv.reader(trace, delimiter=','):
                    operation, block_address, disk_id = item[
                        0], int(item[1], 0), int(item[2], 0)
                    self.sim_read(disk_id, block_address)
                    # print self.ssd.keys()
                    # pdb.set_trace()
            self.print_stats()
            return True
        except IOError as error:
            print("ERROR: Error loading trace: " +
                  error.filename + os.linesep +
                  " with error: " + error.message + os.linesep)
            return False
