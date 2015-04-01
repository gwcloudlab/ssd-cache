from __future__ import division
from cache_entry import Cache_entry
from collections import defaultdict
from collections import OrderedDict
from hyperloglog import HyperLogLog
from rank_mattson_rd import Rank_mattson_rd
# from pprint import pprint
from cache import Cache
from time import time
import hrc_curve


class Multilevel_weighted_lru(Cache):

    def __init__(self, vm_ids):
        Cache.__init__(self)
        self.reuse_distance = Rank_mattson_rd()
        self.vm_ids = vm_ids
        self.no_of_vms = len(vm_ids)
        self.time_interval = 5000
        self.timeout = self.time_interval * 5
        self.ri = defaultdict()
        self.block_lookup = defaultdict(lambda: defaultdict(OrderedDict))
        self.size_lookup = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = defaultdict()
        default_ssd_weight = int(self.maxsize_ssd / self.no_of_vms)
        default_pcie_weight = int(self.maxsize_pcie_ssd / self.no_of_vms)
        self.weight_pcie_ssd = defaultdict(lambda: default_pcie_weight)
        self.weight_ssd = defaultdict(lambda: default_ssd_weight)
        for x in xrange(self.no_of_vms):
            hyperll = HyperLogLog(0.01)
            self.unique_blocks[x] = hyperll

    def timing(f):
        def wrap(*args):
            time1 = time()
            ret = f(*args)
            time2 = time()
            print '%s took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
            return ret
        return wrap

    def sim_read(self, time_of_access, disk_id, block_address):
        """
        This will handle the initial read of a block address
        and tell us when to calculate reuse distances and
        reuse intensities
        """
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        self.reuse_distance.calculate_rd(disk_id, block_address)
        self.handle_hit_miss_evict(disk_id, block_address)

        if time_of_access > self.timeout:
            # Increase the time count
            self.timeout = time_of_access + self.time_interval

            # Calculate RD and get annealed values
            rd_values = self.reuse_distance.get_rd_values()
            rd_cdf = hrc_curve.compute_HRC(rd_values)
            relative_weight_pcie_ssd, \
                relative_weight_ssd = hrc_curve.anneal(rd_cdf,
                                                       self.maxsize_pcie_ssd,
                                                       self.maxsize_ssd)
            self.calculate_weight(relative_weight_pcie_ssd,
                                  relative_weight_ssd)

            print "\t pcie weight: ", self.weight_pcie_ssd,
            print "\t ssd weight: ", self.weight_ssd

            # Calculate Reuse Intensity
            # self.calculate_reuse_intensity()

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

    # @timing
    def handle_hit_miss_evict(self, disk_id, block_address):
        cache_layer = self.item_in_cache(disk_id, block_address)
        if cache_layer is not None:
            self.stats[disk_id, cache_layer, 'hits'] += 1
            if cache_layer == 'pcie_ssd':
                cache_contents = self.block_lookup[disk_id][
                                 cache_layer].pop(block_address)
                self.block_lookup[disk_id][
                                  cache_layer][block_address] = cache_contents
            else:
                removed_item = self.remove_item_from_cache('ssd',
                                                           disk_id,
                                                           block_address)
                self.add_item_to_cache('pcie_ssd',
                                       removed_item['disk_id'],
                                       removed_item['block_address'],
                                       removed_item['cache_contents'])
                if len(self.pcie_ssd) > self.maxsize_pcie_ssd:
                    removed_item = self.remove_item_from_cache('pcie_ssd')
                    self.add_item_to_cache('ssd',
                                           removed_item['disk_id'],
                                           removed_item['block_address'],
                                           removed_item['cache_contents'])
        else:
            self.stats[disk_id, 'total', 'miss'] += 1
            cache_layer = 'pcie_ssd'
            self.add_item_to_cache('pcie_ssd',
                                   disk_id,
                                   block_address,
                                   Cache_entry())
            if len(self.pcie_ssd) > self.maxsize_pcie_ssd:
                removed_item = self.remove_item_from_cache('pcie_ssd')
                self.add_item_to_cache('ssd',
                                       removed_item['disk_id'],
                                       removed_item['block_address'],
                                       removed_item['cache_contents'])
                if len(self.ssd) > self.maxsize_ssd:
                    removed_item = self.remove_item_from_cache('ssd')

    # @timing
    def add_item_to_cache(self, cache_layer, disk_id,
                          block_address, cache_contents):
        if cache_layer == 'pcie_ssd':
            self.pcie_ssd[(disk_id, block_address)] = cache_contents
        else:
            self.ssd[(disk_id, block_address)] = cache_contents
        self.size_lookup[(disk_id, cache_layer)] += 1
        # It is just a lookup, we don't need a value
        # Can change this to a set instead of a dict.
        self.block_lookup[disk_id][cache_layer][block_address] = None

    # @timing
    def remove_item_from_cache(self, cache_layer,
                               disk_id=None, block_address=None):
        if disk_id is None:
            disk_id = self.find_id_to_evict(cache_layer)
            block_address, rd = self.block_lookup[disk_id][
                                cache_layer].popitem(last=False)
        else:
            del self.block_lookup[disk_id][cache_layer][block_address]

        if cache_layer == 'pcie_ssd':
            cache_contents = self.pcie_ssd.pop((disk_id, block_address))
        else:
            cache_contents = self.ssd.pop((disk_id, block_address))

        self.stats[disk_id, cache_layer, 'evicts'] += 1
        self.size_lookup[(disk_id, cache_layer)] -= 1

        return {'disk_id': disk_id,
                'block_address': block_address,
                'cache_contents': cache_contents}

    # @timing
    def find_id_to_evict(self, cache_layer):
        for (disk_id, layer), count in self.size_lookup.iteritems():
            if layer == cache_layer:
                weight = eval("self.weight_" + cache_layer)[disk_id]
                if count > weight:
                    return disk_id

        print cache_layer
        print self.size_lookup

        raise ValueError("There is no ID found to be evicted")

    def pad_zeros(self, undersized_dict):
        # If there is an assigned weight. It is possible to have
        # Percentage: 9%{0: 9821.0, 1: 0} {0: 11738.0, 1: 0}
        # Percentage: 9%{0: 834.0} {0: 834.0} -> there is no
        # 1 here so we cannot evict 1. Instead we evict 0 but
        # intellegently assign 0 all the disk space.
        for disk in self.vm_ids:
            if disk not in undersized_dict.keys():
                undersized_dict[disk] = 0
        return undersized_dict

    def calculate_weight(self, pcie, ssd):
        # self.ri_priority = {k: v / sum(self.ri.values())
        #                     for k, v in self.ri.items()}

        if self.no_of_vms > len(pcie):
            self.pad_zeros(pcie)
        if self.no_of_vms > len(ssd):
            self.pad_zeros(ssd)

        # >>> ssd = {0: 2, 1: 3}
        # >>> maxsize = 10
        # >>> {k: v/sum(ssd.values())*maxsize for k, v in ssd.items()}
        # {0: 4.0, 1: 6.0}
        self.weight_pcie_ssd = {k: int(v / sum(pcie.values()) *
                                self.maxsize_pcie_ssd)
                                for k, v in pcie.items()}
        self.weight_ssd = {k: int(v / sum(ssd.values()) *
                           self.maxsize_ssd)
                           for k, v in ssd.items()}

        # print "Weight for pcie ssd: "
        # pprint (dict(self.weight_pcie_ssd))
        # print "Weight for ssd: "
        # pprint (dict(self.weight_ssd))
        # print "Actual size occupied: "
        # pprint (dict(self.size_lookup))

    def print_stats(self):
        hrc_curve.print_stats('Multi_weighted', self.stats)
