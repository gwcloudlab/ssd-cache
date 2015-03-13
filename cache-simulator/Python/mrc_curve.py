from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from random import randint


class Hrc_curve():
    def __init__(self):
        self.rd_dict = defaultdict(list)

    def compute_HRC(self, rd_values):
        self.update_rd_dict(rd_values)
        self.compute_ecdf()
        self.draw_cdf()

    def update_rd_dict(self, rd_values):
        for disk in rd_values.iterkeys():
            self.rd_dict[disk] += rd_values[disk]

    def compute_ecdf(self):
        for disk in self.rd_dict.iterkeys():
            sorted_array = np.sort(self.rd_dict[disk][:])
            yvals = np.arange(len(sorted_array))/float(len(sorted_array))
            plt.plot(sorted_array, yvals)

    def draw_cdf(self):
        plt.show()


def main():
    hrc = Hrc_curve()
    rd_values = defaultdict(list)
    for x in xrange(50):
        rd_values[1].append(randint(1, 50))
    hrc.compute_HRC(rd_values)

if __name__ == '__main__':
    main()
