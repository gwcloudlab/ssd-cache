from cache_entry import Cache_entry
from cache import Cache
from collections import defaultdict

class Multilevel_weighted_lru(Cache):

    def __init__(self, no_of_vms):
        Cache.__init__(self)
        self.no_of_vms = no_of_vms
        self.block_lookup = {}
        self.rd_blocks = defaultdict(list)
        self.size_lookup = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.weight = defaultdict(lambda: 1000)

    def sim_read(self, time_of_access, disk_id, block_address):
        """
        This will handle the intial read of a block address
        and tell us when to calculate reuse distances and 
        reuse intensities
        """
        self.total_accesses[disk_id] += 1
        #self.unique_blocks[disk_id].add(str(block_address))
        self.handle_hit_miss_evict(disk_id, block_address)
        #self.calculate_reuse_distance(UUID)
        #if time_of_access > self.timeout:
            #pass

    def handle_hit_miss_evict(self, disk_id, block_address):
        try:
            cache_layer = self.block_lookup[(disk_id, block_address)]
            self.stats[disk_id, cache_layer, 'hits'] += 1
            if cache_layer == 'pcie_ssd':
                self.rd_blocks[(disk_id, cache_layer)].remove(block_address)
                self.rd_blocks[(disk_id, 'pcie_ssd')].append(block_address)
            else:
                removed_item = self.remove_item_from_cache('ssd', disk_id, block_address)
                self.add_item_to_cache( 'pcie_ssd', removed_item['disk_id'], 
                                    removed_item['block_address'], removed_item['cache_contents'])
                removed_item = self.remove_item_from_cache('pcie_ssd')
                self.add_item_to_cache( 'ssd', removed_item['disk_id'], 
                                    removed_item['block_address'], removed_item['cache_contents'])
        except KeyError:
            self.stats[disk_id, 'miss'] += 1
            cache_layer = 'pcie_ssd'
            self.add_item_to_cache('pcie_ssd', disk_id, block_address, Cache_entry())
            removed_item = self.remove_item_from_cache('pcie_ssd')
            self.add_item_to_cache( 'ssd', removed_item['disk_id'], 
                                removed_item['block_address'], removed_item['cache_contents'])
            removed_item = self.remove_item_from_cache('ssd', disk_id, block_address)

    def add_item_to_cache(self, cache_layer, disk_id, block_address, cache_contents):
        if cache_layer == 'pcie_ssd':
            self.pcie_ssd[(disk_id, block_address)] = cache_contents
        else:
            self.ssd[(disk_id, block_address)] = cache_contents
        self.rd_blocks[(disk_id, cache_layer)].append(block_address)
        self.size_lookup[(disk_id, cache_layer)] += 1
        self.block_lookup[(disk_id, block_address)] = cache_layer

    def remove_item_from_cache(self, cache_layer, disk_id=None, block_address=None):
        if disk_id == None:
            disk_id = self.find_id_to_evict(cache_layer)
            block_address = self.rd_blocks[(disk_id, cache_layer)][0] 
        self.rd_blocks[(disk_id, cache_layer)].remove(block_address)
        if cache_layer == 'pcie_ssd':
            cache_contents = self.pcie_ssd.pop(disk_id, block_address)
        else:
            cache_contents = self.ssd.pop(disk_id, block_address)
        self.size_lookup[(disk_id, cache_layer)] -= 1
        del self.block_lookup[(disk_id, block_address)]
        return { 'disk_id':disk_id, 
                 'block_address': block_address, 
                 'cache_contents': cache_contents }

    def find_id_to_evict(self, cache_layer):
        for ids, count in self.size_lookup.iteritems():
            if ids[1] == cache_layer:
                if count >= self.weight[ids]:
                    return ids
        return 1
        # return rand.randint(self.no_of_vms) # to evict a random VM
