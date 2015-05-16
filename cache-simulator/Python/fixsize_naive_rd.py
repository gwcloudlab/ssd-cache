from collections import defaultdict

class Fixsize_naive_rd():
    def __init__(self, max_cache_size):
        self.rd = defaultdict(lambda: defaultdict(list))
        self.rd_list = defaultdict(list)
        self.rd_dict = defaultdict(defaultdict)
        self.rd_size_lookup = defaultdict(lambda: 0)
        self.rd_size_max = max_cache_size #{0:100000, 1:100000, 2:100000, 3:100000} # max cache size for each disc

    def calculate_rd(self, disk_id, block_address):
        if block_address in self.rd_dict[disk_id]:
            indx = self.rd_list[disk_id].index(block_address)
            self.rd_list[disk_id].pop(indx)
            self.rd_list[disk_id].append(block_address)
            no_of_entries = self.rd_size_lookup[disk_id]
            rd_value = no_of_entries - indx - 1
        else:
	    # Maintain the fix size rd list.
            # For rd larger than max cache size, it will be evicted fron rd list. 
            # set the evicted block's rd equals infinfity which have done when it first access.
	    if self.rd_size_lookup[disk_id]==self.rd_size_max[disk_id]:
                evicted_block_address=self.rd_list[disk_id].pop(0) #rd larger than max cache size
                self.rd_size_lookup[disk_id] -= 1
                del self.rd_dict[disk_id][evicted_block_address]
            rd_value = 999999999
            self.rd_list[disk_id].append(block_address)
            self.rd_size_lookup[disk_id] += 1
            index=self.rd_size_lookup[disk_id]-1
            self.rd_dict[disk_id][block_address]=index

        self.rd[disk_id][block_address].append(rd_value)

    def get_rd_values(self):
        rd_array = defaultdict(list)
        for disk in self.rd:
            for block in self.rd[disk]:
                rd_array[disk] += self.rd[disk][block]
        # self.rd.clear()
        # self.rd_size_lookup.clear()
        # self.rd_list.clear()
        return rd_array
