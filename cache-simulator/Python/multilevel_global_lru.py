from __future__ import division
from cache_entry import Cache_entry
import pprint
from cache import Cache
from collections import OrderedDict, defaultdict
import hyperloglog

class Multilevel_global_lru(Cache):

    def __init__(self, no_of_vms):
        Cache.__init__(self)
        self.no_of_vms = no_of_vms
        self.maxsize_pcie_ssd = 10000
        self.maxsize_ssd = 100000
        self.pcie_ssd = OrderedDict()
        self.ssd = OrderedDict()
        self.ri = defaultdict(lambda: -1)
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = {}
        for x in xrange(self.no_of_vms):
            hyperll = hyperloglog.HyperLogLog(0.01)
            self.unique_blocks[x] = hyperll
        self.time_window = 500
        self.timeout = 0
        self.normalized_intensities = defaultdict(lambda: 0)

    def sim_read(self, time_of_access, disk_id, block_address):
        UUID = (disk_id, block_address)
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        if time_of_access > self.timeout:
            self.timeout = time_of_access + self.time_window
            self.calculate_reuse_intensity()
            self.total_accesses = defaultdict(lambda: 0)
            for x in xrange(self.no_of_vms):
                hyperll = hyperloglog.HyperLogLog(0.01)
                self.unique_blocks[x] = hyperll
            pprint.pprint(dict(self.normalized_intensities))

        if self.normalized_intensities[disk_id] > 0.5:
            if (UUID in self.pcie_ssd):
                cache_contents = self.pcie_ssd.pop(UUID)
                self.pcie_ssd[UUID] = cache_contents
                self.pcie_ssd[UUID].set_lru()
                self.stats[disk_id, "pcie_hits"] += 1
            else:
                new_cache_block = Cache_entry()
                if len(self.pcie_ssd) >= self.maxsize_pcie_ssd:
                    self.pcie_ssd.popitem(last=False)
                    self.stats[disk_id, "pcie_evictions"] += 1
                self.pcie_ssd[UUID] = new_cache_block
                self.stats[disk_id, "pcie_misses"] += 1
        else:
            if (UUID in self.ssd):
                cache_contents = self.ssd.pop(UUID)
                self.ssd[UUID] = cache_contents
                self.ssd[UUID].set_lru()
                self.stats[disk_id, "ssd_hits"] += 1
            else:
                new_cache_block = Cache_entry()
                if len(self.ssd) >= self.maxsize_ssd:
                    self.ssd.popitem(last=False)
                    self.stats[disk_id, "ssd_evictions"] += 1
                self.ssd[UUID] = new_cache_block
                self.stats[disk_id, "ssd_misses"] += 1

    def calculate_reuse_intensity(self):
        self.normalized_intensities = defaultdict(lambda: 0)
        for x in self.unique_blocks.keys():
            if len(self.unique_blocks[x]):
                self.ri[x] = self.total_accesses[x] / (self.time_window * len(self.unique_blocks[x]))
        max_value = max( self.ri.itervalues())
        for key, value in self.ri.items():
            self.normalized_intensities[key] = value / max_value

    def print_stats(self):
        print "\nMultilevel Global LRU:\n"
        print "Maxsize of pcie ssd: ", self.maxsize_pcie_ssd, "\n"
        print "Maxsize of ssd: ", self.maxsize_ssd, "\n"
        pprint.pprint(dict(self.stats))
        # print self.ssd.keys()
