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
        self.rd = defaultdict(defaultdict)
        self.rd_blocks = defaultdict(list)
        self.rd_size = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = {}
        for x in xrange(self.no_of_vms):
            hyperll = hyperloglog.HyperLogLog(0.01)
            self.unique_blocks[x] = hyperll
        self.time_window = 500
        self.timeout = 0
        self.normalized_intensities = defaultdict(lambda: 0)

    def calculate_reuse_distance(self, disk_id, block_address):
        if block_address in self.rd[disk_id]:
            indx = self.rd_blocks.index(block_address)
            del self.rd_blocks[disk_id][index]
            self.rd_blocks[disk_id].append(block_address)
            self.rd[disk_id][block_address] = self.rd_size[disk_id] - indx - 1
        else:
            self.rd_blocks[disk_id].append(block_address)
            self.rd[disk_id][block_address] = -1
            self.rd_size[disk_id] += 1

    def sim_read(self, time_of_access, disk_id, block_address):
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        self.calculate_reuse_distance(disk_id, block_address)
        if time_of_access > self.timeout:
            self.timeout = time_of_access + self.time_window
            self.calculate_reuse_intensity()
            self.calculate_reuse_distance()
            self.total_accesses = defaultdict(lambda: 0)
            for x in xrange(self.no_of_vms):
                hyperll = hyperloglog.HyperLogLog(0.01)
                self.unique_blocks[x] = hyperll
            pprint.pprint(dict(self.normalized_intensities))

        if (block_address in self.pcie_ssd[disk_id]):
            cache_contents = self.pcie_ssd[disk_id].pop(UUID)
            self.pcie_ssd[disk_id][block_address] = cache_contents
            self.pcie_ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "pcie_hits"] += 1
        elif (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(UUID)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "ssd_hits"] += 1
        else:
            new_cache_block = Cache_entry()
            if sum(self.pcie_counter.values()) > self.pcie_maxsize:
                id_to_evice = self.find_id_to_evict(disk_id, block_address)
            # This is the crux of our algorithm and yet to be implemented


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
