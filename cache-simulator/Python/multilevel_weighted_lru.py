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

    def handle_hit_miss_evict():
        try:
            cache_layer = self.block_lookup(UUID)
            cache = eval(cache_layer)
            self.stats[disk_id, cache_layer, 'hits'] += 1
        except KeyError:
            self.stats[disk_id, 'miss'] += 1
            cache_layer = 'pcie_ssd'
            self.block_lookup(UUID) = cache_layer
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
        self.size_lookup[(disk_id, cache_layer)] += 1
        id_to_evict = find_id_to_evict()
        if id_to_evict:
            self.size_lookup[(id_to_evict, cache_layer)] -= 1
