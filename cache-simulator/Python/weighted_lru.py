from __future__ import division
from collections import Counter, defaultdict, OrderedDict
from rank_mattson_rd import Rank_mattson_rd
from cache_entry import Cache_entry
from operator import itemgetter
from cache import Cache
import hyperloglog
import hrc_curve
import time


class Weighted_lru(Cache):

    def __init__(self, vm_ids):
        Cache.__init__(self)
        self.ssd = defaultdict(OrderedDict)
        self.reuse_distance = Rank_mattson_rd()
        self.anneal = defaultdict()
        # Number of cache items currently owned by each disk
        self.counter = defaultdict(lambda: 0)
        self.no_of_vms = len(vm_ids)
        self.ri = defaultdict()  # Reuse intensity
        self.time_interval = 5000   # t_w from vCacheShare 500
        self.timeout = self.time_interval * 5  # Sentinel
        self.total_accesses = defaultdict(lambda: 0)
        # Set to use RI values only to calculate priority
        self.ri_only_priority = False
        self.unique_blocks = {}
        for x in xrange(self.no_of_vms):
            hyperll = hyperloglog.HyperLogLog(0.01)
            self.unique_blocks[x] = hyperll

    def timing(f):
        def wrap(*args):
            time1 = time.time()
            ret = f(*args)
            time2 = time.time()
            print '%s took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
            return ret
        return wrap

    def sim_read(self, time_of_access, disk_id, block_address):
        self.total_accesses[disk_id] += 1
        self.stats[disk_id]["total_accesses"] += 1
        self.unique_blocks[disk_id].add(str(block_address))
        self.reuse_distance.calculate_rd(disk_id, block_address)
        if time_of_access > self.timeout:
            self.timeout = time_of_access + self.time_interval
            self.calculate_reuse_intensity()
            rd_values = self.reuse_distance.get_rd_values()
            rd_cdf = hrc_curve.compute_HRC(rd_values)
            relative_weight_ssd = \
                hrc_curve.single_tier_anneal(rd_cdf, self.maxsize)
            self.calculate_weight(relative_weight_ssd)

        if (block_address in self.ssd[disk_id]):
            cache_contents = self.ssd[disk_id].pop(block_address)
            self.ssd[disk_id][block_address] = cache_contents
            self.ssd[disk_id][block_address].set_lru()
            self.stats[disk_id]["total_hits"] += 1
        else:
            new_cache_block = Cache_entry()
            # If the given disk has no space
            if sum(self.counter.values()) > self.maxsize:
                id_to_evict = self.find_id_to_evict(disk_id, block_address)
                try:
                    self.ssd[id_to_evict].popitem(last=False)
                except KeyError:
                    print self.counter.values(), "\n",
                    print self.weight, "\n", id_to_evict
                    exit(1)
                self.counter[id_to_evict] -= 1
                self.stats[id_to_evict]["total_evictions"] += 1
            self.ssd[disk_id][block_address] = new_cache_block
            self.ssd[disk_id][block_address].set_lru()
            self.counter[disk_id] += 1
            self.stats[disk_id]["total_misses"] += 1

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
                self.ri[disk] = (self.total_accesses[disk] /
                                 (len(self.unique_blocks[disk]) *
                                 self.time_interval))

    def calculate_weight(self, ssd):
        """
        Calculate the weight of each VM/Disk based on their Priorities.
        The Priorities are calculated from their reuse intensity values.
        priority[disk] = ri / sum of ri's for all disks - normalized by sum.
        weight[disk] = priority * max size of the cache.
        For now, there is no upper bound.

        TO-DO: Calculate priorities using RD as well.

        if self.ri_only_priority:
            self.priority = {k: v / sum(self.ri.values())
                             for k, v in self.ri.items()}
        else:
            # else it is either just rd or rd + ri. This is decided in
            # the function construct rd_cdf
            self.priority = {k: v / sum(self.anneal.values())
                             for k, v in self.anneal.items()}
        """

        self.weight = {k: int(v / sum(ssd.values()) * self.maxsize)
                       for k, v in ssd.items()}
        if __debug__:
            print "Weight: ", self.weight, "\n"
