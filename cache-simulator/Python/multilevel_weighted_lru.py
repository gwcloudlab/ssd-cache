from cache_entry import Cache_entry
from cache import Cache
from collection import defaultdict

class Multilevel_weighted_lru(Cache):

    def __init__(self, no_of_vms):
        Cache.__init__(self)
        self.no_of_vms = no_of_vms
        self.block_lookup = {}
        self.size_lookup = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.weight = defaultdict(lamda: 1000)

def sim_read(self, time_of_access, disk_id, block_address):
        """
        This will handle the intial read of a block address
        and tell us when to calculate reuse distances and 
        reuse intensities
        """
        UUID = (disk_id, block_address)
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        self.calculate_reuse_distance(UUID)
        if time_of_access > self.timeout:
            pass

    def remove_item_from_cache(self, cache_layer, disk_id=None, block_address=None):
        if disk_id == None:
            disk_id = find_id_to_evict(cache_layer)
            block_address = self.rd_blocks[(disk_id, cache_layer)][0] 
        self.rd_blocks[(disk_id, cache_layer)].remove(block_address)
        self.eval(cache_layer).pop(disk_id, block_address)
        self.size_lookup[(disk_id, cache_layer)] -= 1
        del self.block_lookup[(disk_id, block_address)]

    def add_item_to_cache(self, cache_layer, disk_id, block_address, cache_contents):
        self.eval(cache_layer)[(disk_id, block_address)] = cache_contents
        self.rd_blocks[(disk_id, cache_layer)].append(block_address)
        self.size_lookup[(disk_id, cache_layer)] += 1
        self.block_lookup[(disk_id, block_address)] = cache_layer

    def handle_hit_miss_evict(self, UUID):
        try:
            cache_layer = self.block_lookup(UUID)
            #cache = eval(cache_layer)
            self.stats[disk_id, cache_layer, 'hits'] += 1
            if cache_layer == 'pcie_ssd':
                self.rd_blocks[(disk_id, cache_layer)].remove(block_address)
                self.rd_blocks[(disk_id, 'pcie_ssd')].append(block_address)
            else:
                #evict item from ssd
                #remove item from ssd list
                removed_item = remove_item_from_cache('ssd', disk_id, block_address)
                #add removed item to pcie
                #append removedj item to pcie list
                    #change the values on the lookup tables
                add_item_to_cache('pcie_ssd', disk_id, block_address, removed_item)
                #evict item from pcie ssd based on LRU
                #remove item from pcie ssd list
                removed_item = remove_item_from_cache('pcie_ssd', disk_id, block_address)
                #add removed item to ssd
                #append removed item to ssd list
                    #change the values on the lookup tables
                    #May be changing the values need to be done only once?
                add_item_to_cache('ssd', disk_id, block_address, removed_item)
        except KeyError:
            self.stats[disk_id, 'miss'] += 1
            cache_layer = 'pcie_ssd'
            #calculate weights and find items to evict on both caches
            #add item to pcie ssd
            #append item to pcie list
                #change the values on the lookup tables
            add_item_to_cache('pcie_ssd', disk_id, block_address, removed_item)
            #evict item from pcie ssd based on LRU
            #remove item from pcie ssd list
                #change the values on the lookup tables
            removed_item = remove_item_from_cache('pcie_ssd', disk_id, block_address)
            #add removed item to ssd
            #append removed item to ssd list
            add_item_to_cache('ssd', disk_id, block_address, removed_item)
            #remove item from ssd based on LRU
            #remove item from ssd list
                #change the values on the lookup tables
                #May be changing the values need to be done only once?
            removed_item = remove_item_from_cache('ssd', disk_id, block_address)


    def find_ids_to_evict(self, cache_layer, disk_id):
        """
        This will take in the input of a disk id that will
        be added to the top most cache level and give as
        output the ids needed to be evicted at each cache
        layer
        """
        # Need a table for total size
        # Need a table for currently occupied size
        # Need a table for currenly allocated weight
        # --- Initially assume static weights for each cache layer
        # Consult the list to get the LRU's of an id's block_adress
        for ids, count in self.size_lookup.iteritems():
            if ids[1] == cache_layer:
                if count >= self.weight[ids]:
                    return ids
        return disk_id

