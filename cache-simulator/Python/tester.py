# from rd_cdf import Rd_cdf
# from random import randint
# from sortedcontainers import SortedList
# from collections import defaultdict
# import os
import csv
from time import time
from naive_rd import Naive_rd


def timing(f):
    def wrap(*args):
        time1 = time()
        ret = f(*args)
        time2 = time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap


def run(algorithm, filename):
    with open(filename, 'rb') as trace:
        for item in csv.reader(trace, delimiter=','):
            disk_id = int(item[2])
            block_address = int(item[4])
            algorithm.calculate_rd(disk_id, block_address)
    print algorithm.get_rd_values()


@timing
def main():
    filename = 'MSR/tiny_usr.csv'
    # rd = defaultdict(SortedList)
    # for x in xrange(4):
    #     for y in xrange(50):
    #         val = randint(1, 10)
    #         rd[x].add(val)
    # dist = Rd_cdf(rd)
    # dist.construct_rd_cdf()
    rd_calculate = Naive_rd()
    algorithms = [rd_calculate]
    for algorithm in algorithms:
        run(algorithm, filename)

if __name__ == '__main__':
    main()
