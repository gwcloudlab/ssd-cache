from __future__ import division
from cache_entry import Cache_entry
from statsmodels import api as sm
import os
import pprint
from cache import Cache
from operator import itemgetter
from collections import Counter, defaultdict, OrderedDict
from numpy import linspace


class Weighted_lru(Cache):

    def __init__(self):
        Cache.__init__(self)
        # Number of cache items currently owned by each disk
        self.counter = defaultdict(lambda: 0)
        self.total_accesses = defaultdict(lambda: 0)
        self.unique_blocks = defaultdict(set)
        self.rd = defaultdict(OrderedDict)  # Reuse distance
        self.ri = defaultdict()  # Reuse intensity
        self.anneal = defaultdict()
        self.time_interval = 50  # t_w from vCacheShare
        self.timeout = 0  # Sentinel
        self.ri_only_priority = True # Set to use RI values only to calculate priority

    def sim_read(self, time_of_access, disk_id, block_address):
        self.total_accesses[disk_id] += 1
        self.unique_blocks[disk_id].add(block_address)
        self.calculate_reuse_distance(disk_id, block_address)
        if time_of_access > self.timeout:
            self.timeout = time_of_access + self.time_interval
            self.calculate_reuse_intensity()
            self.construct_rd_cdf()
            self.calculate_weight()
        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id, "hits"] += 1
        else:
            new_cache_block = Cache_entry()
            # If the given disk has no space
            if sum(self.counter.values()) > self.maxsize:
                id_to_evict = self.find_id_to_evict(disk_id, block_address)
                try:
                    self.ssd[id_to_evict].popitem(last=False)
                except KeyError:
                    print self.counter.values(), "\n", self.weight, "\n", id_to_evict
                    exit(1)
                self.counter[id_to_evict] -= 1
                self.stats[id_to_evict, "evictions"] += 1
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.counter[disk_id] += 1
            self.stats[disk_id, "misses"] += 1

    def find_id_to_evict(self, disk_id, block_address):
        delta = Counter(self.counter) - Counter(self.weight)
        try:
            id_to_be_evicted = max(delta.iteritems(), key=itemgetter(1))[0]
        except ValueError:
            # If all items are exactly equal to their weight,
            # delta would be an empty sequence, hence ValueError.
            id_to_be_evicted = disk_id
        return id_to_be_evicted

    def calculate_reuse_intensity(self):
        """
        Reuse Intensity = S_{total} / (t_w * S_unique)
        self.ri[disk] = float value
        """
        for disk in xrange(self.no_of_vms):
            if len(self.unique_blocks[disk]) == 0:
                # If S_unique is 0, then the priority is set to 0
                self.ri[disk] = 0
            else:
                self.ri[disk] = (self.total_accesses[disk]
                                 / (len(self.unique_blocks[disk])
                                    * self.time_interval))

        self.total_accesses.clear()
        self.unique_blocks.clear()

    def calculate_reuse_distance(self, disk_id, block_address):
        """
        For each block, the RD is calculated by the number of unique blocks
        accessed between two consecutive accesses of the block .
        The initial value of a new block is set to 0 and if that block is
        accessed again, it's index(position) in the list is obtained and
        it is moved to the end of the list. The value (new RD) of this block
        will be the number of blocks between it's index and it's current
        position (which is always at the end of the list).

        self.rd[disk] = ordereddict{ block_address : RD value }
        """
        if block_address in self.rd[disk_id]:
            indx = self.rd[disk_id].keys().index(block_address)
            self.rd[disk_id].pop(block_address)
            sz = len(self.rd[disk_id])
            self.rd[disk_id][block_address] = sz - indx
        else:
            self.rd[disk_id][block_address] = 0

    def construct_rd_cdf(self):
        """
        The estimated hit ratio for each disk is calculated from it's RD by
        first constructing a list ("histogram") of all RD values for each disk,
        i.e., All the RD values (one value per block) is copied into a list.
        The cdf of each of the list is calculated by using the
        sm.distributions' ECDF library function.
        """

        # calculate the normalized rd array
        rd_array = {}
        cdf_x = {}  # The x axis of the cdf
        cdf_y = {}  # The y axis of the cdf. i.e. the hit ratio
        # initialize min and max rd values. This is the x-axis values
        min_rd_value = 0.0
        with open(os.path.join('traces', 'wlru.dat'), 'w') as out_file:
            # Initialize all the header info for the out_file
            out_file.write(" " + str(len(self.rd)) + " " + str(500) + " " + str(1) + "\n ")
            out_file.write(str(150) + "\n")
            # Set a flag to only run sa_anneal if cdf has data
            cdf_not_empty = False
            for disk, block in self.rd.iteritems():
                if sum(block.itervalues()) == 0:
                    max_rd_value = 0.0
                else:
                    cdf_not_empty = True
                    max_rd_value = self.maxsize
                rd_array[disk] = sorted(block.itervalues())
                ecdf = sm.distributions.ECDF(rd_array[disk])
                cdf_x[disk] = linspace(min_rd_value, max_rd_value, 500)  # 500 x tics
                cdf_y[disk] = ecdf(cdf_x[disk])

                if not self.ri_only_priority:
                    # Add ri values to rd
                    cdf_y[disk] += 100 * self.ri[disk]

                out_file.write(" " + str(disk + 1) + "\n")
                for x_axis, y_axis in zip(cdf_x[disk], cdf_y[disk]):
                    out_file.write(" " + str('%.2f' % y_axis) + " " + str('%.2f' % x_axis) + "\n")

        if cdf_not_empty:
            os.system("./sim_anneal")
            sa_solution = [line.strip() for line in open("sa_solution.txt", 'r')]
            sa_solution = map(int, sa_solution)

            for disk, sa_value in zip(cdf_x, sa_solution):
                self.anneal[disk] =  cdf_y[disk][sa_value]

    def calculate_weight(self):
        """
        Calculate the weight of each VM/Disk based on their Priorities.
        The Priorities are calculated from their reuse intensity values.
        priority[disk] = ri / sum of ri's for all disks - normalized by sum.
        weight[disk] = priority * max size of the cache.
        For now, there is no upper bound.

        TO-DO: Calculate priorities using RD as well.
        """
        if self.ri_only_priority:
            self.priority = {k: v / sum(self.ri.values())
                         for k, v in self.ri.items()}
        else:
            # else it is either just rd or rd + ri. This is decided in
            # the function construct rd_cdf
            self.priority = {k: v / sum(self.anneal.values())
                         for k, v in self.anneal.items()}

        self.weight = {k: int(v * self.maxsize)
                       for k, v in self.priority.items()}

    def print_stats(self):
        print "\nWeighted LRU:\n"
        print "Weight: ", self.weight, "\n"
        pprint.pprint(dict(self.stats))
