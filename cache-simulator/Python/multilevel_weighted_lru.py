from __future__ import division
from cache_entry import Cache_entry
from collections import defaultdict
from collections import OrderedDict
from hyperloglog import HyperLogLog
from cache import Cache
from pprint import pprint
from time import time

class Multilevel_weighted_lru(Cache):

    def __init__(self, no_of_vms):
        Cache.__init__(self)
        self.no_of_vms = no_of_vms
        self.time_interval = 500
        self.timeout = 0
        self.ri = defaultdict()
        self.rd = 0 # In future this should be replaced with original rd
        self.block_lookup = defaultdict(lambda: defaultdict(OrderedDict))
        self.size_lookup = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.weight = defaultdict(lambda: 0)
        self.unique_blocks = defaultdict()
        for x in xrange(self.no_of_vms):
            hyperll = HyperLogLog(0.01)
            self.unique_blocks[x] = hyperll

    def sim_read(self, time_of_access, disk_id, block_address):
        """
        This will handle the initial read of a block address
        and tell us when to calculate reuse distances and 
        reuse intensities
        """
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        self.handle_hit_miss_evict(disk_id, block_address)
        #self.calculate_reuse_distance(disk_id, block_address)
        if time_of_access > self.timeout:
            self.timeout = time_of_access + self.time_interval
            self.calculate_reuse_intensity()
            self.calculate_weight()

    def timing(f):
        def wrap(*args):
            time1 = time()
            ret = f(*args)
            time2 = time()
            #print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
            return ret
        return wrap

    def calculate_reuse_intensity(self):
        for disk in xrange(self.no_of_vms):
            unique_element_count = len(self.unique_blocks[disk])
            if unique_element_count == 0:
                self.ri[disk] = 0
            else:
                self.ri[disk] = (self.total_accesses[disk] / 
                                (unique_element_count) * self.time_interval)

    def item_in_cache(self, disk_id, block_address):
        for layer in self.block_lookup[disk_id].keys():
            if block_address in self.block_lookup[disk_id][layer]:
                return layer
        return None

    @timing
    def handle_hit_miss_evict(self, disk_id, block_address):
        cache_layer = self.item_in_cache(disk_id, block_address)
        if cache_layer is not None:
            self.stats[disk_id, cache_layer, 'hits'] += 1
            if cache_layer == 'pcie_ssd':
                cache_contents = self.block_lookup[disk_id][cache_layer].pop(block_address)
                self.block_lookup[disk_id][cache_layer][block_address] = cache_contents
            else:
                removed_item = self.remove_item_from_cache('ssd', disk_id, block_address)
                self.add_item_to_cache( 'pcie_ssd', removed_item['disk_id'], 
                                    removed_item['block_address'], removed_item['cache_contents'])
                if len(self.pcie_ssd) > self.maxsize_pcie_ssd:
                    removed_item = self.remove_item_from_cache('pcie_ssd')
                    self.add_item_to_cache( 'ssd', removed_item['disk_id'], 
                                    removed_item['block_address'], removed_item['cache_contents'])
        else:
            self.stats[disk_id, 'miss'] += 1
            cache_layer = 'pcie_ssd'
            self.add_item_to_cache('pcie_ssd', disk_id, block_address, Cache_entry())
            if len(self.pcie_ssd) > self.maxsize_pcie_ssd:
                removed_item = self.remove_item_from_cache('pcie_ssd')
                self.add_item_to_cache( 'ssd', removed_item['disk_id'], 
                                removed_item['block_address'], removed_item['cache_contents'])
                if len(self.ssd) > self.maxsize_ssd:
                    removed_item = self.remove_item_from_cache('ssd')

    #@timing
    def add_item_to_cache(self, cache_layer, disk_id, block_address, cache_contents):
        if cache_layer == 'pcie_ssd':
            self.pcie_ssd[(disk_id, block_address)] = cache_contents
        else:
            self.ssd[(disk_id, block_address)] = cache_contents
        self.size_lookup[(disk_id, cache_layer)] += 1
        self.block_lookup[disk_id][cache_layer][block_address] = self.rd

    @timing
    def remove_item_from_cache(self, cache_layer, disk_id=None, block_address=None):
        if disk_id == None:
            disk_id = self.find_id_to_evict(cache_layer)
            block_address, rd = self.block_lookup[disk_id][cache_layer].popitem(last=False)
        else:
            del self.block_lookup[disk_id][cache_layer][block_address]

        #del self.block_lookup[disk_id][cache_layer][block_address]
        if cache_layer == 'pcie_ssd':
            cache_contents = self.pcie_ssd.pop((disk_id, block_address)) #double parenthesis are imp.
        else:
            cache_contents = self.ssd.pop((disk_id, block_address))

        self.stats[disk_id, cache_layer , 'evicts'] += 1
        self.size_lookup[(disk_id, cache_layer)] -= 1

        return { 'disk_id': disk_id, 
                 'block_address': block_address, 
                 'cache_contents': cache_contents }

    #@timing
    def find_id_to_evict(self, cache_layer):
        for (disk_id, layer), count in self.size_lookup.iteritems():
            if layer == cache_layer:
                if count > eval("self.weight_" + cache_layer)[disk_id]:
                    return disk_id
        # return rand.randint(self.no_of_vms) # to evict a random VM

    def calculate_weight(self):
        self.priority = {k: v / sum(self.ri.values()) for k, v in self.ri.items()}
        self.weight_ssd = {k: int(v * self.maxsize_ssd) for k, v in self.priority.items()}
        self.weight_pcie_ssd = {k: int(v * self.maxsize_pcie_ssd) for k, v in self.priority.items()}
        print "Priority: "
        pprint (dict(self.priority))
        print "Weight for pcie ssd: "
        pprint (dict(self.weight_pcie_ssd))
        print "Weight for ssd: "
        pprint (dict(self.weight_ssd))
        print "Actual size occupied: "
        pprint (dict(self.size_lookup))

    def print_stats(self):
        print "\nMultilevel weighted LRU:\n"
        print "Weight: ", self.weight, "\n"
        pprint(dict(self.stats))
