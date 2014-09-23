'''
Cache simulator
'''
from collections import OrderedDict, defaultdict


class Cache(object):

    def __init__(self, blocksize, cachesize):
        # This will be the actual cache
        self.ssd = defaultdict(OrderedDict)
        self.no_of_vms = 5  # IDs 0 to 4
        self.blocksize = blocksize
        self.cachesize = cachesize
        # max size and self.weight's sum should be equal
        # self.maxsize = cachesize / blocksize
        # Assign priority on the scale of 1 to 100
        # self.priority = {0: 80, 1: 10, 2: 7, 3: 1, 4: 1, 5: 1}
        # self.weight = Counter({k: int(v * self.maxsize / 100)
        #                      for k, v in self.priority.items()})
        # self.weight = Counter({1: 1038989, 2: 17514932, 3: 167835})
        # self.weight = Counter({1: 103898, 2: 1751493, 3: 16783})
        # Baseline values
        self.weight = defaultdict(lambda: 100000)
        self.maxsize = 1000000  # 1 million cache entries
        self.stats = defaultdict(lambda: 0)

    def delete(self):
        self.resetCache()

    # Zero out cache blocks/flags/values
    def resetCache(self):
        self.ssd.clear()
