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


class IndexedOrderedDict(OrderedDict):

    """
    This is a custom class that combines the properties of
    Dictionary, deque and counter. Dictionary + deque = OrderedDict
    is a good data structure for implementing a LRU cache. When items
    are added, it always adds it at the end of the Dictionary and items
    can be popped from the front or arbitrarily.

    This is combined further with a Counter, which increases the value of
    a given keyword (in our case, the disk_id) by 1 when it is inserted and
    decrease by 1 when deleted.

    This saves us from a lot of trouble using a separate datastructure to
    store it and making the program ugly with a ton of if else conditionals.
    """

    def __init__(self, key=lambda k: k, *args, **kwargs):
        self.counter = Counter()
        self.key_transform = key
        super(IndexedOrderedDict, self).__init__(*args, **kwargs)

    def __delitem__(self, key):
        super(IndexedOrderedDict, self).__delitem__(key)
        self.counter[self.key_transform(key)] -= 1

    def __setitem__(self, key, value):
        if key not in self:
            self.counter[self.key_transform(key)] += 1

        super(IndexedOrderedDict, self).__setitem__(key, value)


class Sim(object):

    def __init__(self, filename=None, blocksize=4096, cachesize=196608000):
        # There is a total of ~48K unique block addresses in the input file.
        self.EVICT_POLICY = "weightedLRU"
        # This will be the actual cache
        self.ssd = IndexedOrderedDict(key=lambda k: k[1])
        self.filename = filename
        self.blocksize = blocksize
        self.cachesize = cachesize
        # max size and self.weight's sum should be equal
        self.maxsize = cachesize / blocksize
        self.weight = {0: 16000, 1: 16000, 2: 16000}
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

    def checkFreeSpace(self, UUID):
        if (len(self.ssd) < self.maxsize):
            if self.EVICT_POLICY == "staticLRU":
                return self.ssd.counter[UUID[1]] < self.weight[UUID[1]]
            else:  # Both global and weighted LRU care only about maxsize
                return True
        return False

    def sim_read(self, UUID):
        if (UUID in self.ssd):
            cache_contents = self.ssd.pop(UUID)
            self.ssd[UUID] = cache_contents
            self.ssd[UUID].set_lru()
            self.state["hits"] += 1
            self.stats[UUID[1], "hits"] += 1
        else:
            self.insert(UUID)
            self.state["misses"] += 1
            self.stats[UUID[1], "misses"] += 1

    def insert(self, UUID):
        new_cache_block = cache.Cache()
        if self.checkFreeSpace(UUID):
            self.ssd[UUID] = new_cache_block
            self.ssd[UUID].set_lru()
        else:
            self.evictItem(UUID)
            self.ssd[UUID] = new_cache_block
            self.ssd[UUID].set_lru()
            self.state["evictions"] += 1
            self.stats[UUID[1], "evictions"] += 1

    def evictItem(self, UUID):
        if self.EVICT_POLICY == "weightedLRU":
            delta = Counter(self.ssd.counter) - Counter(self.weight)
            # Negative values are ignored in the above expression.
            # We don't need them. To not ignore use:
            # delta =  k: self.ssd.counter.get(k, 0) - self.weight.get(k, 0)
            # for k in set(self.ssd.counter) & set(self.weight) }
            try:
                id_to_be_evicted = max(delta.iteritems(), key=itemgetter(1))[0]
            except ValueError:
                # If all items are exactly equal to their weight,
                # delta would be an empty sequence, hence ValueError.
                self.ssd.popitem(last=False)
            else:
                for item_to_be_evicted in self.ssd.keys():
                    if item_to_be_evicted[1] == id_to_be_evicted:
                        self.ssd.pop(item_to_be_evicted)
                        break
        elif self.EVICT_POLICY == "staticLRU":
            # pop the first element that matches with the disk id
            for item_to_be_evicted in self.ssd.keys():
                if item_to_be_evicted[1] == UUID[1]:
                    self.ssd.pop(item_to_be_evicted)
                    break
        else:
            self.ssd.popitem(last=False)

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
                    disk_id, block_address, read_size, operation, \
                        time_of_access = item[0], item[1], int(item[2], 0), \
                        item[3], float(item[4])
                    UUID = (block_address, disk_id)
                    self.sim_read(UUID)
                    # print self.ssd.keys()
                    # pdb.set_trace()
            self.print_stats()
            return True
        except IOError as error:
            print("ERROR: Error loading trace: " +
                  error.filename + os.linesep +
                  " with error: " + error.message + os.linesep)
            return False
