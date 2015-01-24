'''
Cache simulator
'''
from collections import OrderedDict, defaultdict


class Cache(object):

    def __init__(self):
        # This will be the actual cache. It is a nested dict.
        # Default dict is the disk ID and the ordered dict are
        # the blocks inside the disk.
        self.ssd = defaultdict(OrderedDict)
        self.no_of_vms = 4  # IDs 0 to 4
        # Baseline values - min cache for each VM
        self.weight = defaultdict(lambda: 10000)
        # ~ 1 million cache entries
        self.maxsize = sum(self.weight.values()) + 100000
        self.stats = defaultdict(lambda: 0)

    def delete(self):
        self.resetCache()

    # Zero out cache blocks/flags/values
    def resetCache(self):
        self.ssd.clear()
