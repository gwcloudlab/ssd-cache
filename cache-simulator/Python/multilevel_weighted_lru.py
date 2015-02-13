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

    def remove_item_from_cache(self, cache_layer, disk_id, block_address):
        self.eval(cache_layer).pop(disk_id, block_address)
        self.rd_blocks[(disk_id, cache_layer)].remove(block_address)
        self.size_lookup[(disk_id, cache_layer)] -= 1
        del self.block_lookup[(disk_id, block_address)]

    def handle_hit_miss_evict():
        try:
            cache_layer = self.block_lookup(UUID)
            #cache = eval(cache_layer)
            self.stats[disk_id, cache_layer, 'hits'] += 1
            if cache_layer == 'pcie_ssd':
                indx = self.rd_blocks[(disk_id, cache_layer)].index(block_address)
                del self.rd_blocks[(disk_id, cache_layer)][indx]
                self.rd_blocks[(disk_id, 'pcie_ssd')].append(block_address)
            else:
                #evict item from ssd
                #remove item from ssd list
                #add removed item to pcie
                #append removed item to pcie list
                    #change the values on the lookup tables
                #evict item from pcie ssd based on LRU
                #remove item from pcie ssd list
                #add removed item to ssd
                #append removed item to ssd list
                    #change the values on the lookup tables
                    #May be changing the values need to be done only once?
        except KeyError:
            self.stats[disk_id, 'miss'] += 1
            cache_layer = 'pcie_ssd'
            #calculate weights and find items to evict on both caches
            #add item to pcie ssd
            #append item to pcie list
                #change the values on the lookup tables
            #evict item from pcie ssd based on LRU
            #remove item from pcie ssd list
                #change the values on the lookup tables
            #add removed item to ssd
            #append removed item to ssd list
            #remove item from ssd based on LRU
            #remove item from ssd list
                #change the values on the lookup tables
                #May be changing the values need to be done only once?
            self.block_lookup(UUID) = cache_layer
            self.rd_blocks[(disk_id, cache_layer)].append(block_address)
            new_cache_block = Cache_entry()
            self.pcie_ssd[UUID] = new_cache_block
            find_ids_to_evict(disk_id)
            self.size_lookup[(disk_id, cache_layer)] += 1
            cache = eval(cache_layer)

    def find_ids_to_evict(self, disk_id):
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
        ids_to_be_evicted = []
        self.size_lookup[(disk_id, cache_layer)] += 1
        for ids, counts in self.counter.iteritems():
            if counts > self.weight[ids]:
                ids_to_be_evicted.append(ids)

