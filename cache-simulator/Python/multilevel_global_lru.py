from __future__ import division
from cache_entry import Cache_entry
from collections import defaultdict
from collections import OrderedDict
from cache import Cache
from time import time


class Multilevel_global_lru(Cache):

    def __init__(self, vm_ids):
        Cache.__init__(self)
        self.vm_ids = vm_ids
        self.no_of_vms = len(vm_ids)
        self.block_lookup = defaultdict(OrderedDict)

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
        else:
            # The item is a miss. So,
            # (1) Add item to pcie
            # (2) Evict lru item from pcie and add it to ssd
            # (3) Evict the lru item from ssd.
            self.stats[disk_id]['total_miss'] += 1
            cache_contents = Cache_entry()
            self.block_lookup['pcie_ssd'][UUID] = cache_contents
            if len(self.block_lookup['pcie_ssd']) > self.maxsize_pcie_ssd:
                cache_contents = self.block_lookup[
                                'pcie_ssd'].popitem(last=False)
                self.block_lookup['ssd'][UUID] = cache_contents

            if len(self.block_lookup['ssd']) > self.maxsize_pcie_ssd:
                cache_contents = self.block_lookup['ssd'].popitem(last=False)

    def item_in_cache(self, UUID):
        for layer in self.block_lookup.iterkeys():
            if UUID in self.block_lookup[layer]:
                return layer
        return None
