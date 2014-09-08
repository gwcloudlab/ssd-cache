'''
Cache simulator
'''
from collections import OrderedDict, defaultdict


class Sim(object):

    def __init__(self, filename=None, blocksize=8, cachesize=80):
        self.EVICT_POLICY = "staticLRU"
        # This will be the actual cache
        self.ssd = defaultdict(OrderedDict)
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

    def delete(self):
        self.resetCache()

    # Zero out cache blocks/flags/values
    def resetCache(self):
        self.ssd.clear()
