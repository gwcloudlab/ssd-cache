from __future__ import division
from cache_entry import Cache_entry
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
from pprint import pprint
from cache import Cache
from time import time
import hrc_curve


class Multilevel_global_lru(Cache):

    def __init__(self, vm_ids):
        Cache.__init__(self)
        self.vm_ids = vm_ids
        self.no_of_vms = len(vm_ids)
        self.block_lookup = defaultdict(OrderedDict)
        self.time_interval = 3600
        self.interval = 0
        self.timeout = 0
        self.ri = defaultdict()  # To make data consistent in detailstats for pruning
        # self.weight_ssd = defaultdict(lambda: 0)
        # self.weight_pcie_ssd = defaultdict(lambda: 0)
        for vm in self.vm_ids:
            self.ri[vm] = 0
            self.weight_ssd[vm] = 0
            self.weight_pcie_ssd[vm] = 0
        if __debug__:
            with open('log/detailed_stats_global.log', 'a') as out_file:
                out_file.write('Algorithm,Multi-level-global-LRU\n')
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
        self.stats[disk_id]['total_accesses'] += 1
        UUID = (disk_id, block_address)
        cache_layer = self.item_in_cache(UUID)
        if cache_layer:
            # The item is a hit. So, regardless of which layer the item
            # resides on, we pop it and add it to pcie.
            self.stats[disk_id]['total_hits'] += 1
            self.stats[disk_id][str(cache_layer) + '_hits'] += 1
            cache_contents = self.block_lookup[cache_layer].pop(UUID)
            self.block_lookup['pcie_ssd'][UUID] = cache_contents
            if cache_layer == 'ssd':
                # If the hit item is on ssd, we have already evicted it. So,
                # add an evicted item from pcie to ssd and evict ssd's lru item
                if len(self.block_lookup['pcie_ssd']) > self.maxsize_pcie_ssd:
                    cache_contents = self.block_lookup[
                        'pcie_ssd'].popitem(last=False)
                    self.block_lookup['ssd'][UUID] = cache_contents
                    disk_popped = cache_contents[0][0]
        else:
            # The item is a miss. So,
            # (1) Add item to pcie
            # (2) Evict lru item from pcie and add it to ssd
            # (3) Evict the lru item from ssd.
            self.stats[disk_id]['total_miss'] += 1
            cache_contents = Cache_entry()
            self.block_lookup['pcie_ssd'][UUID] = cache_contents
            if len(self.block_lookup['pcie_ssd']) > self.maxsize_pcie_ssd:
                self.stats[disk_id]['pcie_ssd_evicts'] += 1
                cache_contents = self.block_lookup[
                    'pcie_ssd'].popitem(last=False)
                self.block_lookup['ssd'][UUID] = cache_contents
                disk_popped = cache_contents[0][0]

                if len(self.block_lookup['ssd']) > self.maxsize_ssd:
                    cache_contents = self.block_lookup['ssd'].popitem(last=False)
                    disk_popped = cache_contents[0][0]
                    self.stats[disk_popped]['ssd_evicts'] += 1

        if time_of_access > self.timeout:
            self.interval += 1

            # Increase the time count
            self.timeout = time_of_access + self.time_interval

            for vm in self.vm_ids:
                self.weight_ssd[vm] = 0
                self.weight_pcie_ssd[vm] = 0

            for layer, vms in self.block_lookup.iteritems():
                for vm in vms.iterkeys():
                    if layer == 'pcie_ssd':
                        self.weight_pcie_ssd[vm[0]] += 1
                    else:
                        self.weight_ssd[vm[0]] += 1

            if __debug__:
                with open('log/detailed_stats_global.log', 'a') as out_file:
                    out_file.write("Interval," + str(self.interval) + '\n')
                    out_file.write("pcie_weight,")
                    pprint(dict(self.weight_pcie_ssd), out_file)
                    out_file.write("ssd_weight,")
                    pprint(dict(self.weight_ssd), out_file)
                    out_file.write("reuse_intensity,")
                    pprint(dict(self.ri), out_file)
                    hrc_curve.print_per_interval_stats(self.stats, out_file)

    def item_in_cache(self, UUID):
        for layer in self.block_lookup.iterkeys():
            if UUID in self.block_lookup[layer]:
                return layer
        return None
