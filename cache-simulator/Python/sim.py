'''
Cache simulator
'''

import collections
import os
import cache
import csv


class IndexedOrderedDict(collections.OrderedDict):

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
        self.counter = collections.Counter()
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

    def __init__(self, filename=None, blocksize=16, cachesize=256):
        self.constsize = 4  # For now all VMs get 4 slots
        self.EVICT_POLICY = "staticLRU"
        self.ssd = IndexedOrderedDict()  # This will be the actual cache
        self.filename = filename
        self.blocksize = blocksize
        self.cachesize = cachesize
        self.maxsize = cachesize / blocksize
        self.counter = {}
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
        if self.EVICT_POLICY == "globalLRU":
            if (len(self.ssd) <= self.maxsize):
                return True
            else:
                return False
        elif self.EVICT_POLICY == "staticLRU":
            if (len(self.ssd) <= self.maxsize
                    and self.ssd.counter[UUID[1]] <= self.constsize):
                return True
            else:
                return False

    def sim_write(self, UUID):
        pass

    def sim_read(self, UUID):
        if ((UUID) in self.ssd):
            cache_contents = self.ssd.pop(UUID)
            self.ssd[UUID] = cache_contents
            self.ssd[UUID].set_lru()
            self.state["hits"] += 1
        else:
            self.insert(UUID)
            self.state["misses"] += 1

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

    def evictItem(self, UUID):
        if self.EVICT_POLICY == "globalLRU":
            self.ssd.popitem(last=False)
        elif self.EVICT_POLICY == "staticLRU":
            # pop the first element that matches with the disk id
            for item in self.ssd.keys():
                if item[1] == UUID[1]:
                    self.ssd.pop(item)

    def delete(self):
        self.resetCache()

    def print_stats(self):
        print self.config
        print self.state
        print self.ssd

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
                    UUID = (block_address, disk_id)
                    if operation == 'r':
                        self.sim_read(UUID)
                    else:
                        self.sim_write(UUID)
            self.print_stats()
            return True
        except IOError as error:
            print("ERROR: Error loading trace: " +
                  error.filename + os.linesep +
                  " with error: " + error.message + os.linesep)
            return False
