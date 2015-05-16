from rank_mattson_rd import Rank_mattson_rd
from counterstack_rd import CounterStack_rd
from naive_rd import Naive_rd
from fixsize_naive_rd import Fixsize_naive_rd
from offline_parda_rd import Offline_parda_rd
from basic_shards_rd import Basic_shards_rd
from time import time
import hrc_curve
import cProfile
import csv
import sys
import os


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
        file_size = os.stat(filename).st_size
        bytes_read = 0
        # time_interval = 5000
        # timeout = 5000
        for item in csv.reader(trace, delimiter=','):

            bytes_read += 37
            percent = bytes_read*100 / file_size
            sys.stdout.write('\r Percentage: ' + str(percent) + '%')
            sys.stdout.flush()
            # time_of_access = int(item[0])
            disk_id = int(item[2])
            block_address = int(item[4])
            algorithm.calculate_rd(disk_id, block_address)
            # if time_of_access > timeout:
            # timeout = time_of_access + time_interval
    rd_values = algorithm.get_rd_values()
    rd_cdf = hrc_curve.compute_HRC(rd_values)
    # annealed_values = hrc_curve.single_tier_anneal(rd_cdf)
    # print annealed_values
    hrc_curve.draw_figure('Rank Mattson', rd_cdf)


def main():
    """
    all_files = ['hm.csv', 'mds.csv', 'prn.csv', 'proj.csv',
                 'prxy.csv', 'rsrch.csv', 'src.csv', 'stg.csv',
                 'ts.csv', 'usr.csv', 'wdev.csv', 'web.csv']
    """
    #pr = cProfile.Profile()
    #pr.enable()

    all_files = ['hm.csv']#tiny_hm.csv
    for name in all_files:
        print name
        filename = os.path.join('MSR', name)
        rank_mattson = Rank_mattson_rd()
        counterstack = CounterStack_rd()
        # naive_rd = Naive_rd()
        offline_parda = Offline_parda_rd()
        basic_shards = Basic_shards_rd(0.01) #the input is sample_rate such as 0.01, 0.001, 0.0001
        max_cache_size = {0:100000, 1:100000, 2:100000, 3:100000}
        fixsize_naive = Fixsize_naive_rd(max_cache_size) #the input is max cache size for each disc such as {0:100000, 1:100000, 2:100000, 3:100000}
        algorithms = [fixsize_naive]
        for algorithm in algorithms:
            run(algorithm, filename)

    #pr.disable()
    #pr.print_stats(sort='time')

if __name__ == '__main__':
    main()
