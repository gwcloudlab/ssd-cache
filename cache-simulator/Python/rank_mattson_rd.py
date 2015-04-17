from collections import defaultdict


class Rank_mattson_rd():
    def __init__(self):
        self.rd = defaultdict(lambda: defaultdict(list))
        self.index_tracker = 0

    def calculate_rd(self, disk_id, block_address):
        self.index_tracker += 1
        self.rd[disk_id][block_address].append(self.index_tracker)

    def get_rd_values(self):
        rd_array = defaultdict(list)
        for disk in self.rd.iterkeys():
            for block in self.rd[disk].iterkeys():
                block_rd = self.rd[disk][block]
                if len(block_rd) > 1:
                    for idx in xrange(len(block_rd) - 1):
                        rd_array[disk].append(block_rd[idx+1] - block_rd[idx])
                rd_array[disk].append(9999999999)
        # self.rd.clear()
        return rd_array
