from collections import OrderedDict
from cache_entry import Cache_entry
from cache import Cache


class Global_lru(Cache):

    def __init__(self, vm_ids, cache_size):
        Cache.__init__(self)
        self.maxsize = cache_size
        print "\ncache size: ", self.maxsize
        self.vm_ids = vm_ids
        self.no_of_vms = len(self.vm_ids)
        self.ssd = OrderedDict()

    def sim_read(self, time_of_access, disk_id, block_address):
        UUID = (disk_id, block_address)
        self.stats[disk_id]['total_accesses'] += 1
        if (UUID in self.ssd):
            cache_contents = self.ssd.pop(UUID)
            self.ssd[UUID] = cache_contents
            self.ssd[UUID].set_lru()
            self.stats[disk_id]["total_hits"] += 1
        else:
            new_cache_block = Cache_entry()
            if(len(self.ssd) >= self.maxsize):
                self.ssd.popitem(last=False)
                self.stats[disk_id]["total_evictions"] += 1
            self.ssd[UUID] = new_cache_block
            self.stats[disk_id]["total_misses"] += 1
