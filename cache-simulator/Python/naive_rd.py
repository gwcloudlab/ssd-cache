from collections import defaultdict
from collections import OrderedDict


class Naive_rd():
    def __init__(self):
        self.rd = dict(OrderedDict)
        self.rd_list = defaultdict(lambda: list)
        self.rd_size_lookup = defaultdict(lambda: 0)

    def calculate_rd(self, disk_id, block_address):
        if block_address in self.rd[disk_id]:
            indx = self.rd_list[disk_id].index(block_address)
            self.rd_list[disk_id].pop(indx)
            self.rd_list[disk_id].append(block_address)
            no_of_entries = self.size_lookup[disk_id]
            rd_value = no_of_entries - indx + 1
        else:
            rd_value = -1
            self.size_lookup[disk_id] += 1

        self.rd[disk_id][block_address] = rd_value
