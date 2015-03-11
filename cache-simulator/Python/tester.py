# from rd_cdf import Rd_cdf
# from random import randint
# from sortedcontainers import SortedList
# from collections import defaultdict
# import os
import csv
from time import time
from naive_rd import Naive_rd
from cs_rd import Cs_rd
from rd_cdf import Rd_cdf


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
    with open(filename, 'rb') as trace:
        for item in csv.reader(trace, delimiter=','):
            disk_id = int(item[2])
            block_address = int(item[4])
            algorithm.calculate_rd(disk_id, block_address)
    rd_values = algorithm.get_rd_values()
    print rd_values
    # test_cdf = Rd_cdf(rd_values)
    # print test_cdf.construct_rd_cdf()


def main():
    filename = 'MSR/wdev.csv'
    # rd = defaultdict(SortedList)
    # for x in xrange(4):
    #     for y in xrange(50):
    #         val = randint(1, 10)
    #         rd[x].add(val)
    # dist = Rd_cdf(rd)
    # dist.construct_rd_cdf()
    naive_rd = Naive_rd()
    cs_rd = Cs_rd(4)
    algorithms = [naive_rd, cs_rd]
    for algorithm in algorithms:
        run(algorithm, filename)

if __name__ == '__main__':
    main()
