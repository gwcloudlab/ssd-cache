'''
Cache simulator
'''
from collections import OrderedDict, defaultdict, Counter


class Cache(object):

    def __init__(self, blocksize, cachesize):
        # This will be the actual cache
        self.ssd = defaultdict(OrderedDict)
        self.blocksize = blocksize
        self.cachesize = cachesize
        # max size and self.weight's sum should be equal
        self.maxsize = cachesize / blocksize
        # Assign priority on the scale of 1 to 10
        self.priority = {0: 3, 1: 2, 2: 2, 3: 1, 4: 1, 5: 1}
        self.weight = Counter({k: int(v * self.maxsize / 10)
                              for k, v in self.priority.items()})
        self.stats = defaultdict(lambda: 0)

    def delete(self):
        self.resetCache()

    # Zero out cache blocks/flags/values
    def resetCache(self):
        self.ssd.clear()
