from __future__ import division
from cache_entry import Cache_entry
from collections import defaultdict
from collections import OrderedDict
from hyperloglog import HyperLogLog
from datetime import datetime
# from rank_mattson_rd import Rank_mattson_rd
# from counterstack_rd import CounterStack_rd
from offline_parda_rd import Offline_parda_rd
from cache import Cache
from time import time
import hrc_curve
from pprint import pprint


class Multilevel_weighted_lru(Cache):

    def __init__(self, vm_ids):
        Cache.__init__(self)
        self.reuse_distance = Offline_parda_rd()
        # self.reuse_distance = Rank_mattson_rd()
        # self.reuse_distance = CounterStack_rd()
        self.vm_ids = vm_ids
        self.no_of_vms = len(vm_ids)
        self.interval = 0
        self.time_interval = 3600
        self.timeout = 0
        self.ri = defaultdict()
        self.block_lookup = defaultdict(lambda: defaultdict(OrderedDict))
        self.size_lookup = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = defaultdict()
        default_ssd_weight = int(self.maxsize_ssd / self.no_of_vms)
        default_pcie_weight = int(self.maxsize_pcie_ssd / self.no_of_vms)
        self.weight_pcie_ssd = defaultdict(lambda: default_pcie_weight)
        self.weight_ssd = defaultdict(lambda: default_ssd_weight)
        for vm in self.vm_ids:
            self.weight_pcie_ssd[vm] = default_pcie_weight
            self.weight_ssd[vm] = default_ssd_weight

        for vm in self.vm_ids:
            hyperll = HyperLogLog(0.01)
            self.unique_blocks[vm] = hyperll
        if __debug__:
            with open('log/detailed_stats.log', 'a') as out_file:
                out_file.write('Algorithm,Multi-level-weighted-LRU\n')
                out_file.write('CurrentTime,' + str(datetime.now()) + '\n')

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
        self.total_accesses[disk_id] += 1  # Will be cleared every interval
        self.stats[disk_id]['total_accesses'] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        self.reuse_distance.calculate_rd(disk_id, block_address)
        self.handle_hit_miss_evict(disk_id, block_address)

        if time_of_access > self.timeout:
            self.interval += 1

            # Increase the time count
            self.timeout = time_of_access + self.time_interval

            # Calculate RD and get annealed values
            rd_values = self.reuse_distance.get_rd_values()
            rd_cdf = hrc_curve.compute_HRC(rd_values)
            self.calculate_reuse_intensity()

            # Clear interval specific counters
            self.total_accesses.clear()
            self.unique_blocks.clear()
            for vm in self.vm_ids:
                hyperll = HyperLogLog(0.01)
                self.unique_blocks[vm] = hyperll

            relative_weight_pcie_ssd, relative_weight_ssd = \
                hrc_curve.multi_tier_anneal(rd_cdf,
                                            self.ri,
                                            self.maxsize_pcie_ssd,
                                            self.maxsize_ssd)

            self.calculate_weight(relative_weight_pcie_ssd,
                                  relative_weight_ssd)

            if __debug__:
                with open('log/detailed_stats_weighted.log', 'a') as out_file:
                    out_file.write("Interval," + str(self.interval) + '\n')
                    out_file.write("pcie_weight,")
                    pprint(dict(self.weight_pcie_ssd), out_file)
                    out_file.write("ssd_weight,")
                    pprint(dict(self.weight_ssd), out_file)
                    out_file.write("reuse_intensity,")
                    pprint(dict(self.ri), out_file)
                    hrc_curve.print_per_interval_stats(self.stats, out_file)
                    # print "\t RI: ", self.ri

    def calculate_reuse_intensity(self):
        for disk in self.vm_ids:
            unique_element_count = len(self.unique_blocks[disk])
            if unique_element_count == 0:
                self.ri[disk] = 0
            else:
                self.ri[disk] = 1 - (unique_element_count /
                                     self.total_accesses[disk])

    def item_in_cache(self, disk_id, block_address):
        for layer in self.block_lookup[disk_id].keys():
            if block_address in self.block_lookup[disk_id][layer]:
                return layer
        return None

    # @timing
    def handle_hit_miss_evict(self, disk_id, block_address):
        cache_layer = self.item_in_cache(disk_id, block_address)
        if cache_layer:
            self.stats[disk_id]['total_hits'] += 1
            self.stats[disk_id][str(cache_layer) + '_hits'] += 1
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
            self.stats[disk_id]['total_miss'] += 1
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

        self.stats[disk_id][str(cache_layer) + '_evicts'] += 1
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

        # If workload is truly random just use previously used weights
        if sum(pcie.values()) == 0 or sum(ssd.values()) == 0:
            return

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
