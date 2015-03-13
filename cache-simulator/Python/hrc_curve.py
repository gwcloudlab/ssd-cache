from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from random import randint


def compute_HRC(rd_dict):
    """
    http://stackoverflow.com/questions/3209362/
    how-to-plot-empirical-cdf-in-matplotlib-in-python
    """
    for disk in rd_dict.iterkeys():
        sorted_array = np.sort(rd_dict[disk][:])
        yvals = np.arange(len(sorted_array))/float(len(sorted_array))
        plt.plot(sorted_array, yvals)

def draw_cdf():
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
