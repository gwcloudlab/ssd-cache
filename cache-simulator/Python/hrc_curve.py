from statsmodels import api as sm
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np


lines = ['-', '--', '-.', ':']
linecycler = cycle(lines)


def compute_HRC(rd_dict, draw=False):
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

        if draw:
            draw_figure(x_vals, y_vals, disk)


def draw_figure(x_vals, y_vals, disk):
    plt.plot(x_vals, y_vals,
             next(linecycler),
             linewidth=2.0,
             label="Disk: " + str(disk))


def draw_cdf(name):
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
