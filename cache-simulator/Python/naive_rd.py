from collections import defaultdict


class Naive_rd():
    def __init__(self):
        self.rd = defaultdict(lambda: defaultdict(list))
        self.rd_list = defaultdict(list)
        self.rd_size_lookup = defaultdict(lambda: 0)

    def calculate_rd(self, disk_id, block_address):
        if block_address in self.rd[disk_id]:
            indx = self.rd_list[disk_id].index(block_address)
            self.rd_list[disk_id].pop(indx)
            self.rd_list[disk_id].append(block_address)
            no_of_entries = self.rd_size_lookup[disk_id]
            rd_value = no_of_entries - indx + 1
        else:
            rd_value = 999999999
            self.rd_list[disk_id].append(block_address)
            self.rd_size_lookup[disk_id] += 1

        self.rd[disk_id][block_address].append(rd_value)

    def get_rd_values(self):
        rd_array = defaultdict(list)
        for disk in self.rd:
            for block in self.rd[disk]:
                rd_array[disk] += self.rd[disk][block]
        self.rd.clear()
        return rd_array
