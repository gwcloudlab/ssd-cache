from rank_mattson_rd import Rank_mattson_rd
from time import time
import hrc_curve
import csv
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
        for item in csv.reader(trace, delimiter=','):
            disk_id = int(item[2])
            block_address = int(item[4])
            algorithm.calculate_rd(disk_id, block_address)
    rd_values = algorithm.get_rd_values()
    rd_cdf = hrc_curve.compute_HRC(rd_values)
    annealed_values = hrc_curve.anneal(rd_cdf)
    print annealed_values
    hrc_curve.draw_figure('Rank Mattson', rd_cdf)


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
        rank_mattson = Rank_mattson_rd()
        algorithms = [rank_mattson]
        for algorithm in algorithms:
            run(algorithm, filename)

if __name__ == '__main__':
    main()
