from __future__ import division
from collections import defaultdict
from statsmodels import api as sm
import matplotlib.pyplot as plt
from itertools import cycle
from cache import Cache
import numpy as np
import os


def compute_HRC(rd_dict):
    cache = Cache()

    rd_cdf = defaultdict(lambda: defaultdict(list))

    for disk in rd_dict.iterkeys():
        sorted_array = sorted(rd_dict[disk][:])

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
        # x_vals = np.linspace(sorted_array[0], actual_largest, 50)
        x_vals = np.linspace(0, cache.maxsize_pcie_ssd, 100)  # For pcie disk
        x_vals = np.append(x_vals, np.linspace(cache.maxsize_pcie_ssd,
                                               cache.maxsize_ssd,
                                               100))
        y_vals = ecdf(x_vals)

        rd_cdf[disk]['x_axis'] = list(x_vals)
        rd_cdf[disk]['y_axis'] = list(y_vals)

    return rd_cdf


def multi_tier_anneal(rd_cdf, maxsize_pcie_ssd, maxsize_ssd):

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

    sa_solution, \
        optimal_pcie_rd = calculate_optimal_space(rd_cdf, maxsize_pcie_ssd)

    # Reordering data for second pass for ssd layer
    # >>> hit_rate =  [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
    # >>> rd = range(10)
    # >>> optimal_hr = 4
    # >>> hit_rate = hit_rate[optimal_hr:]
    # >>> hit_rate
    # [0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
    # >>> hit_rate.extend(optimal_hr * [hit_rate[-1]])
    # >>> hit_rate
    # [0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.0, 1.0, 1.0, 1.0]
    # >>> rd
    # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    for disk, optimal_rd in zip(rd_cdf.keys(), sa_solution):
        rd_cdf[disk]['y_axis'] = rd_cdf[disk]['y_axis'][optimal_rd:]
        rd_cdf[disk]['y_axis'].extend(optimal_rd*[rd_cdf[disk]['y_axis'][-1]])

    sa_solution, optimal_ssd_rd = calculate_optimal_space(rd_cdf, maxsize_ssd)

    return (optimal_pcie_rd, optimal_ssd_rd)


def single_tier_anneal(rd_cdf, maxsize_ssd):

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

    sa_solution, \
        optimal_ssd_rd = calculate_optimal_space(rd_cdf, maxsize_ssd)

    return optimal_ssd_rd


def calculate_optimal_space(rd_cdf, maxsize):
    write_infile_for_sim_anneal(rd_cdf, maxsize)
    os.system("./sim_anneal")
    sa_solution = [line.strip() for line in open("sa_solution.txt", 'r')]
    sa_solution = map(int, sa_solution)

    optimal_space = {}
    optimal_hr = {}
    for disk, optimal_rd in zip(rd_cdf.keys(), sa_solution):
        optimal_space[disk] = rd_cdf[disk]['x_axis'][optimal_rd]
        optimal_hr[disk] = rd_cdf[disk]['y_axis'][optimal_rd]

    return (sa_solution, optimal_space)


def write_infile_for_sim_anneal(rd_cdf, maxsize):
    n_cdf_points = 200
    n_cache_layers = 1
    with open(os.path.join('traces', 'wlru.dat'), 'w') as out_file:
        out_file.write(' ' + str(len(rd_cdf)) +
                       ' ' + str(n_cdf_points) +
                       ' ' + str(n_cache_layers) + '\n' +
                       ' ' + str(maxsize) + '\n')
        for disk in rd_cdf.keys():
            out_file.write(' ' + str(disk + 1) + '\n')
            for x, y in zip(rd_cdf[disk]['x_axis'], rd_cdf[disk]['y_axis']):
                y *= 100  # sim anneal cpp doesn't work with float
                out_file.write(' ' + str('%.2f' % y) +
                               ' ' + str('%.2f' % x) + '\n')


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


def print_stats(metadata, stats):

    with open(os.path.join('log', 'runs.log'), 'a') as out_file:
        out_file.write("---------------------------------------------\n")
        out_file.write("Configuration:\n")
        for k, v in metadata.iteritems():
            out_file.write('\t' + str(k) + ':\t\t' + str(v) + '\n')

        out_file.write("Statistics:\n")
        for disk in stats.iterkeys():
            out_file.write('Disk ' + str(disk) + ' stats:\n')
            for k, v in stats[disk].iteritems():
                out_file.write('\t' + k + ':\t\t' + str(v) + '\n')
            hitrate = (stats[disk]['total_hits'] /
                       stats[disk]['total_accesses']) * 100
            out_file.write('\tHit Rate:\t' + str('%.2f' % hitrate) + ' %\n')
