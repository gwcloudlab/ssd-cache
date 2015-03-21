# from rd_cdf import Rd_cdf
# from random import randint
# from sortedcontainers import SortedList
# from collections import defaultdict
import os
import csv
from time import time
# from mattson_rd import Mattson_rd
# from counterstack_rd import CounterStack_rd
# from rd_cdf import Rd_cdf
from rank_mattson_rd import Rank_mattson_rd
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
    rd_cdf = hrc_curve.compute_HRC(rd_values)
    annealed_values = hrc_curve.anneal(rd_cdf)
    print annealed_values
    hrc_curve.draw_figure('Rank Mattson', rd_cdf)
    # test_cdf = Rd_cdf(rd_values)
    # print test_cdf.construct_rd_cdf()


def main():
    """
    all_files = ['hm.csv', 'mds.csv', 'prn.csv', 'proj.csv',
                 'prxy.csv', 'rsrch.csv', 'src.csv', 'stg.csv',
                 'ts.csv', 'usr.csv', 'wdev.csv', 'web.csv']
    """
    all_files = ['hm.csv']
    for name in all_files:
        print name
        filename = os.path.join('MSR', name)
        # filename = 'MSR/wdev.csv'  # 1.4K file
        # mattson = Mattson_rd()
        # counterstack = CounterStack_rd()
        rank_mattson = Rank_mattson_rd()
        algorithms = [rank_mattson]
        for algorithm in algorithms:
            run(algorithm, filename)

if __name__ == '__main__':
    main()
