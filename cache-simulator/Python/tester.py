# from rd_cdf import Rd_cdf
# from random import randint
# from sortedcontainers import SortedList
# from collections import defaultdict
# import os
import csv
from time import time
from mattson_rd import Mattson_rd
from rank_mattson_rd import Rank_mattson_rd
from counterstack_rd import CounterStack_rd
from rd_cdf import Rd_cdf
import hrc_curve


def timing(f):
    def wrap(*args):
        time1 = time()
        ret = f(*args)
        time2 = time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap


@timing
def run(algorithm, filename):
    line = 0
    with open(filename, 'rb') as trace:
        for item in csv.reader(trace, delimiter=','):
            line += 1
            disk_id = int(item[2])
            block_address = int(item[4])
            algorithm.calculate_rd(disk_id, block_address)
            # print line,
    rd_values = algorithm.get_rd_values()
    # print rd_values
    alg_name = algorithm.__class__.__name__
    hrc_curve.compute_HRC(alg_name, rd_values)
    # test_cdf = Rd_cdf(rd_values)
    # print test_cdf.construct_rd_cdf()


def main():
    # filename = 'MSR/wdev.csv'  # 1.4K file
    # filename = 'MSR/pre-processed.csv' # 87M
    # filename = 'MSR/mrc_test.csv'  # 51K
    filename = 'MSR/pre.csv'  # 870M
    # rd = defaultdict(SortedList)
    # for x in xrange(4):
    #     for y in xrange(50):
    #         val = randint(1, 10)
    #         rd[x].add(val)
    # dist = Rd_cdf(rd)
    # dist.construct_rd_cdf()
    mattson = Mattson_rd()
    rank_mattson = Rank_mattson_rd()
    counterstack = CounterStack_rd()
    algorithms = [rank_mattson]
    for algorithm in algorithms:
        run(algorithm, filename)
    hrc_curve.draw_cdf()

if __name__ == '__main__':
    main()
