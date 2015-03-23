from collections import defaultdict


class Cache(object):

    def __init__(self):
        # This will be the actual cache. It is a nested dict.
        # Default dict is the disk ID and the ordered dict are
        # the blocks inside the disk.
        self.ssd = {}
        self.pcie_ssd = {}
        # Baseline values - min cache for each VM
        self.weight = defaultdict(lambda: 0)
        self.weight_pcie_ssd = defaultdict(lambda: 0)
        self.weight_ssd = defaultdict(lambda: 0)
        # self.maxsize = sum(self.weight.values()) + 100000
        self.maxsize = 1000000  # 1e6 blocks can fir
        self.maxsize_ssd = 1000000
        self.maxsize_pcie_ssd = 10000  # 10% of ssd cache
        self.stats = defaultdict(lambda: 0)

    def delete(self):
        self.resetCache()

    # Zero out cache blocks/flags/values
    def resetCache(self):
        self.ssd.clear()
        self.pcie_ssd.clear()
