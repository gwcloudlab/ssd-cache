from collections import defaultdict
from sortedcontainers import SortedList
from hyperloglog import HyperLogLog


class Cs_rd():
    def __init__(self):
        self.rd_list = defaultdict(lambda: [0])
        self.deltaX = defaultdict(lambda: [1])
        self.deltaY = defaultdict(lambda: [0])
        self.rd_array = defaultdict(SortedList)
        for x in xrange(self.no_of_vms):
            hyperll = HyperLogLog(0.01)
            self.unique_blocks[x] = hyperll

    def calculate_rd(self, disk_id, block_address):
        unique_count = self.calculate_unique_elements(disk_id, block_address)
        self.rd_list[disk_id].append(unique_count)
        self.calculate_deltaX(disk_id)
        self.calculate_deltaY(disk_id)
        self.get_rd_values(self, disk_id)

    def calculate_unique_elements(self, disk_id, block_address):
        self.unique_blocks[disk_id].add(str(block_address))
        return len(self.unique_blocks[disk_id])

    def calculate_deltaX(self, disk_id):
        last_element = self.rd_list[disk_id][-1] - self.rd_list[disk_id][-2]
        self.deltaX[disk_id].append(last_element)

    def calculate_deltaY(self, disk_id):
        last_element = self.deltaX[-1] - self.deltaX[disk_id][-2]
        self.deltaY[disk_id].append(last_element)

    def get_rd_values(self, disk_id):
        if (self.deltaY[disk_id][-1] != 0):
            self.rd_array[disk_id].add(self.rd_list[disk_id][-1])
        return self.rd_array
    # TODO: return ONLY when an element is being add. In most cases, they are
    # not added.