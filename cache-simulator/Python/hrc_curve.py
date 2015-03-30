from __future__ import division
from collections import defaultdict
from statsmodels import api as sm
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np
from pprint import pprint
import os


def compute_HRC(rd_dict):

    rd_cdf = defaultdict(lambda: defaultdict(list))

    for disk in rd_dict.iterkeys():
        sorted_array = np.sort(rd_dict[disk][:])

        # find the second largest element in the sorted array.
        # ex. sorted_array = [1,2,3,3,3,4,1000,1000,...]
        # We want that 1000 to be included in the cdf but not
        # in the graph.
        actual_largest = sorted_array[-1]
        for element in reversed(sorted_array):
            if element < actual_largest:
                actual_largest = element
                break

        ecdf = sm.distributions.ECDF(sorted_array)
        x_vals = np.linspace(sorted_array[0], actual_largest, 50)  # hardcoded
        y_vals = ecdf(x_vals)

        rd_cdf[disk]['x_axis'] = x_vals
        rd_cdf[disk]['y_axis'] = y_vals

    return rd_cdf


def anneal(rd_cdf):

    """
    Precondition:
        The rd vaules should not be empty
        The rd values should not have all 9999999 values's
    Postcondition:
        Optimal rd vaules for a given cache size
    """
    for disk in rd_cdf:
        if (rd_cdf[disk]['x_axis'][0] > 99999999 or
                rd_cdf[disk]['y_axis'][-1] == 0):
            rd_cdf[disk]['x_axis'] = len(rd_cdf[disk]['x_axis'])*[0]

    write_infile_sim_anneal(rd_cdf)
    os.system("./sim_anneal")
    sa_solution = [line.strip() for line in open("sa_solution.txt", 'r')]
    sa_solution = map(int, sa_solution)

    cdf_values = {}
    for disk, optimal_rd in zip(rd_cdf.keys(), sa_solution):
        cdf_values[disk] = rd_cdf[disk]['x_axis'][optimal_rd]

    return cdf_values


def write_infile_sim_anneal(rd_cdf):
    n_cdf_points = 50
    n_cache_layers = 2
    ssd_size = 1000000
    pcie_size = 10000
    with open(os.path.join('traces', 'wlru.dat'), 'w') as out_file:
        out_file.write(' ' + str(len(rd_cdf)) +
                       ' ' + str(n_cdf_points) +
                       ' ' + str(n_cache_layers) + '\n')
        out_file.write(' ' + str(ssd_size) + ' ' + str(pcie_size) + '\n')
        for disk in rd_cdf.keys():
            out_file.write(' ' + str(disk + 1) + '\n')
            for x, y in zip(rd_cdf[disk]['x_axis'], rd_cdf[disk]['y_axis']):
                y *= 100  # sim anneal cpp doesn't work with float
                out_file.write(' ' + str('%.2f' % y) +
                               ' ' + str('%.2f' % x) +
                               ' ' + str('%.2f' % (x/100)) + '\n')


def draw_figure(name, nested_dict):

    lines = ['-', '--', '-.', ':']
    linecycler = cycle(lines)

    for disk in nested_dict.iterkeys():
        plt.plot(nested_dict[disk]['x_axis'], nested_dict[disk]['y_axis'],
                 next(linecycler),
                 linewidth=2.0,
                 label="Disk: " + str(disk))

    plt.xlabel('Cache Size in no. of blocks', fontsize=20)
    plt.ylabel('Hit Ratio', fontsize=20)
    plt.title('CDF', fontsize=20)
    legend = plt.legend(loc='lower right', shadow=True)
    # The frame is a instance surrounding the legend
    # http://matplotlib.org/1.3.1/examples/pylab_examples/legend_demo.html
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    plt.grid(True)
    plt.show()
    plt.savefig(name + '.png')
    plt.clf()


def print_stats(metadata, data):
    stats = defaultdict(lambda: defaultdict(lambda: 0))
    for k, v in data.iteritems():
        if k[2] == 'hits':
            stats[k[0]]['total_hits'] += v
        elif k[2] == 'miss':
            stats[k[0]]['total_misses'] += v

    with open(os.path.join('log', 'runs.log'), 'a') as out_file:
        pprint(dict(metadata), out_file)
        pprint(dict(data), out_file)

        for disk in stats.iterkeys():
            hitrate = (stats[disk]['total_hits'] /
                       (stats[disk]['total_hits'] +
                       stats[disk]['total_misses'])) * 100

            out_file.write("Hit rate of disk " +
                           str(disk) +
                           ' is: ' +
                           str('%.2f' % hitrate) +
                           '\n')
