from collections import defaultdict
from statsmodels import api as sm
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np
from random import randint


def compute_HRC(alg_name, rd_dict):
    lines = ['-', '--', '-.', ':']
    linecycler = cycle(lines)

    for disk in rd_dict.iterkeys():
        sorted_array = np.sort(rd_dict[disk][:])

        # find the second largest element in the sorted array.
        # ex. sorted_array = [1,2,3,3,3,4,1000,1000,...]
        # We want that 1000 to be included in the cdf but not
        # in the graph.
        largest_element = sorted_array[-1]
        for element in reversed(sorted_array):
            if element < largest_element:
                second_largest = element
                break

        ecdf = sm.distributions.ECDF(sorted_array)
        x_vals = np.linspace(sorted_array[0], second_largest, second_largest)
        y_vals = ecdf(x_vals)

        plt.plot(x_vals, y_vals,
                 next(linecycler),
                 linewidth = 2.0,
                 label=alg_name + " disk: " + str(disk))

def draw_cdf():
    plt.xlabel('Cache Size (no. of blocks)', fontsize=20)
    plt.ylabel('Hit Ratio', fontsize=20)
    plt.title('CDF', fontsize=20)
    legend = plt.legend(loc='lower right', shadow=True)
    # The frame is a instance surrounding the legend
    # http://matplotlib.org/1.3.1/examples/pylab_examples/legend_demo.html
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    plt.grid(True)
    plt.xlim([0, 800])
    plt.show()
    # plt.savefig('mattson_vs_counterstack.png')

"""
def main():
    rd_values = defaultdict(list)
    for i in xrange(4):
        for x in xrange(50):
            rd_values[1].append(randint(1, 50))
    compute_HRC(rd_values)
    draw_cdf()

if __name__ == '__main__':
    main()
"""
