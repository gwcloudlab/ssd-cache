import os
from time import time
from statsmodels import api as sm
from numpy import linspace


class Rd_cdf():

    def __init__(self, rd):
        """
        Use a sorted container http://grantjenks.com/docs/sortedcontainers/
        self.rd is of the form {disk_id : [rd array]}
        """
        self.maxsize = 100
        self.rd = rd
        # initialize min and max rd values. This is the x-axis values
        self.min_rd_value = 1.0
        self.no_of_cdf_x_values = 50  # 50 x tics

    def timing(f):
        def wrap(*args):
            time1 = time()
            ret = f(*args)
            time2 = time()
            print '%s took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
            return ret
        return wrap

    def construct_rd_cdf(self):
        """
        The estimated hit ratio for each disk is calculated from it's RD by
        first constructing a list ("histogram") of all RD values for each disk,
        i.e., All the RD values (one value per block) is copied into a list.
        The cdf of each of the list is calculated by using the
        sm.distributions' ECDF library function.
        """

        with open(os.path.join('traces', 'wlru.dat'), 'w') as out_file:
            cdf_x = {}  # The x axis of the cdf
            cdf_y = {}  # The y axis of the cdf. i.e. the hit ratio
            # Initialize all the header info for the out_file
            out_file.write(" " + str(len(self.rd)) + " " +
                           str(self.no_of_cdf_x_values) + " " + str(1) + "\n ")
            out_file.write(str(self.maxsize) + "\n")
            # Set a flag to only run sa_anneal if cdf has data
            cdf_not_empty = False
            for disk, rd_values in self.rd.iteritems():
                if rd_values[-1] == 0:  # If last value is 0 then sum is 0
                    max_rd_value = 0.0
                else:
                    cdf_not_empty = True
                    max_rd_value = self.maxsize
                ecdf = sm.distributions.ECDF(rd_values)
                cdf_x[disk] = linspace(self.min_rd_value,
                                       max_rd_value, self.no_of_cdf_x_values)
                cdf_y[disk] = ecdf(cdf_x[disk])
                cdf_y[disk] *= 100  # CPP program doesn't work well with float

                out_file.write(" " + str(disk + 1) + "\n")
                for x_axis, y_axis in zip(cdf_x[disk], cdf_y[disk]):
                    out_file.write(" " + str('%.2f' % y_axis) +
                                   " " + str('%.2f' % x_axis) + "\n")

        if cdf_not_empty:
            os.system("./sim_anneal")
            # tt = Timer(lambda: os.system("./sim_anneal"))
            # print 'It took %s sec to run sim_anneal' % (tt.timeit(number=1))
            sa_solution = [line.strip()
                           for line in open("sa_solution.txt", 'r')]
            sa_solution = map(int, sa_solution)
            cdf_values = []
            for disk in cdf_x.keys():
                cdf_values.append(cdf_x[disk][sa_solution[disk - 1]])
            return cdf_values
