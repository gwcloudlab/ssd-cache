from collections import defaultdict
from collections import OrderedDict
from sortedcontainers import SortedList


class Naive_rd():
    def __init__(self):
        self.rd = defaultdict(OrderedDict)
        self.rd_list = defaultdict(list)
        self.rd_size_lookup = defaultdict(lambda: 0)

    def calculate_rd(self, disk_id, block_address):
        if block_address in self.rd[disk_id]:
            indx = self.rd_list[disk_id].index(block_address)
            self.rd_list[disk_id].pop(indx)
            self.rd_list[disk_id].append(block_address)
            no_of_entries = self.rd_size_lookup[disk_id]
            rd_value = no_of_entries - indx
        else:
            rd_value = -1
            self.rd_list[disk_id].append(block_address)
            self.rd_size_lookup[disk_id] += 1

        self.rd[disk_id][block_address] = rd_value

    def get_rd_values(self):
        rd_array = defaultdict(SortedList)
        for disk in self.rd.iterkeys():
            for rd_values in self.rd[disk].itervalues():
                rd_array[disk].add(rd_values)
        return rd_array
