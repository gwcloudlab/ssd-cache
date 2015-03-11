from collections import defaultdict
from sortedcontainers import SortedList
from hyperloglog import HyperLogLog


class Cs_rd():
    def __init__(self, no_of_vms):
        self.no_of_vms = no_of_vms
        self.rd_list = defaultdict(list)
        self.deltaX = []
        self.deltaY = []
        self.current_column = []
        self.previous_column = []
        self.rd_array = defaultdict(SortedList)

    def calculate_rd(self, disk_id, block_address):
        self.calculate_unique_matrix(disk_id, block_address)
        self.extract_last_two_columns(disk_id)
        self.calculate_deltaX()
        self.calculate_deltaY()
        self.calculate_rd_values(disk_id)

    def calculate_unique_matrix(self, disk_id, block_address):
        hyperll = HyperLogLog(0.01)
        self.rd_list[disk_id].append(hyperll)
        for item in self.rd_list[disk_id]:
            item.add(str(block_address))

    def extract_last_two_columns(self, disk_id):
        self.previous_column = self.current_column[:]
        self.current_column = []  # May be we can just update/reuse
        for item in self.rd_list[disk_id]:
            self.current_column.append(len(item))

    def calculate_deltaX(self):
        self.deltaX = []
        self.deltaX = [x - y for x, y in
                       zip(self.current_column, self.previous_column)]
        # To compensate for the shorter current_column len.
        self.deltaX.append(1)

    def calculate_deltaY(self):
        self.deltaY = []
        for val in xrange(len(self.deltaX)-1, 0, -1):
            self.deltaY.append(self.deltaX[val] - self.deltaX[val-1])
            # We can stop when we see a value >1

    def calculate_rd_values(self, disk_id):
        for indx in xrange(len(self.deltaY)):
            if self.deltaY[indx] > 0:
                rd = self.current_column[indx]
                self.rd_array[disk_id].add(rd)
                break  # Assuming there will only be one value >1

    def get_rd_values(self):
        return self.rd_array

    # TODO: return ONLY when an element is being add. In most cases,
    # they are not added. We CANNOT check this at the very by
    # comparing unique_count with the last rd_list because
    # we need the repeated element count. Is there a smarter way?
