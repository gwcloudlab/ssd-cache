class Rd_cdf():
    def __init__(self, rd):
        """
        self.rd is of the form {disk_id : [rd array]}
        """
        self.rd = rd
        # initialize min and max rd values. This is the x-axis values
        self.min_rd_value = 1.0
        self.no_of_cdf_x_values = 50
    
    def construct_rd_cdf(self):
        """
        The estimated hit ratio for each disk is calculated from it's RD by
        first constructing a list ("histogram") of all RD values for each disk,
        i.e., All the RD values (one value per block) is copied into a list.
        The cdf of each of the list is calculated by using the
        sm.distributions' ECDF library function.
        """

        with open(os.path.join('traces', 'wlru.dat'), 'w') as out_file:
            # Initialize all the header info for the out_file
            out_file.write(" " + str(len(self.rd)) + " " + str(no_of_cdf_x_values) + " " + str(1) + "\n ")
            out_file.write(str(self.maxsize) + "\n")
            # Set a flag to only run sa_anneal if cdf has data
            cdf_not_empty = False
            for disk, rd_values in self.rd.iteritems():
                cdf_x = {}  # The x axis of the cdf
                cdf_y = {}  # The y axis of the cdf. i.e. the hit ratio
                if rd_values[-1] == 0: # If the last value of a sorted list is 0 then the sum is 0
                    max_rd_value = 0.0
                else:
                    cdf_not_empty = True
                    max_rd_value = self.maxsize
                ecdf = sm.distributions.ECDF(rd_values)
                cdf_x = linspace(self.min_rd_value, max_rd_value, self.no_of_cdf_x_values)# 50 xtics
                cdf_y = ecdf(cdf_x[disk])
                cdf_y *= 100 # CPP program doesn't work well with float

                out_file.write(" " + str(disk + 1) + "\n")
                for x_axis, y_axis in zip(cdf_x[disk], cdf_y[disk]):
                    out_file.write(" " + str('%.2f' % y_axis) + " " + str('%.2f' % x_axis) + "\n")

        if cdf_not_empty:
            os.system("./sim_anneal")
            #tt = Timer(lambda: os.system("./sim_anneal"))
            #print 'It took %s seconds to run sim_anneal' % (tt.timeit(number=1))
            sa_solution = [line.strip() for line in open("sa_solution.txt", 'r')]
            sa_solution = map(int, sa_solution)

            for disk, sa_value in zip(cdf_x, sa_solution):
                self.anneal[disk] = cdf_x[disk][sa_value]
                #print "anneal: ", self.anneal
                #print "sa_solution: ", sa_solution
                #print cdf_x
                #print cdf_y
