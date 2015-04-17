from collections import defaultdict
from hashlib import sha1
from bintrees.avltree import AVLTree

class Basic_shards_rd():
    def __init__(self, sample_rate):
        self.rd = defaultdict(lambda: defaultdict(list))
        self.rd_list = defaultdict(list) # for mattson_rd algorithm
	self.rd_tree = AVLTree() # for balancetree_rd algorithm
	self.rd_hash = defaultdict(defaultdict) # for balancetree_rd algorithm
        self.rd_size_lookup = defaultdict(lambda: 0) # for mattson_rd algorithm
	self.rd_infinity_value = 999999999
	self.rd_sample_rate = sample_rate #0.01, 0.001, 0.0001
	self.hash = sha1()
	self.space = 16777216 #2^24
	self.threshold=self.space*sample_rate

    def calculate_rd(self, disk_id, block_address):	
	self.hash.update(str(block_address))
	hash_value = long(self.hash.hexdigest()[:16], 16)
	#print hash_value
	hash_value = hash_value % self.space
        if hash_value < self.threshold:
	    self.mattson_rd(disk_id, block_address)
	    # self.balancetree_rd(disk_id, block_address)

    def mattson_rd(self, disk_id, block_address):
        if block_address in self.rd[disk_id]:
            indx = self.rd_list[disk_id].index(block_address)
            self.rd_list[disk_id].pop(indx)
            self.rd_list[disk_id].append(block_address)
            no_of_entries = self.rd_size_lookup[disk_id]
            rd_value = no_of_entries - indx + 1
	    rd_value=rd_value/self.rd_sample_rate #back up rd
        else:
            rd_value = self.rd_infinity_value
            self.rd_list[disk_id].append(block_address)
            self.rd_size_lookup[disk_id] += 1

        self.rd[disk_id][block_address].append(rd_value)


    def balancetree_rd(self, disk_id, block_address):
        if block_address in self.rd_hash[disk_id]:
            indx = self.rd_hash[disk_id][block_address]
            self.rd_tree[disk_id].pop(indx)
	    no_of_entries=len(self.rd_tree[disk_id])
            rd_value = no_of_entries - indx
	    rd_value=rd_value/self.rd_sample_rate #scale backup rd
        else:
	    no_of_entries=len(self.rd_tree[disk_id])
	    self.rd_hash[disk_id][block_address]=no_of_entries
	    rd_value = self.rd_infinity_value
	
	self.rd_tree[disk_id][no_of_entries]= 1
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
