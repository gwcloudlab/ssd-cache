from collections import defaultdict
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np
from random import randint


def compute_HRC(alg_name, rd_dict):
    """
    http://stackoverflow.com/questions/3209362/
    how-to-plot-empirical-cdf-in-matplotlib-in-python
    """
    lines = ['-', '--', '-.', ':']
    linecycler = cycle(lines)

    for disk in rd_dict.iterkeys():
        sorted_array = np.sort(rd_dict[disk][:])
        yvals = np.arange(len(sorted_array))/float(len(sorted_array))

        plt.plot(sorted_array, yvals,
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
    plt.show()

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
