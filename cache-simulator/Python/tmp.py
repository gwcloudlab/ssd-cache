import csv
from time import time
from counterstack_rd import CounterStack_rd


def timing(f):
    def wrap(*args):
        time1 = time()
        ret = f(*args)
        time2 = time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap


def main():
    filename = 'MSR/tmp.csv'
    counterstack = CounterStack_rd()
    line = 0
    with open(filename, 'rb') as trace:
        for item in csv.reader(trace, delimiter=','):
            line += 1
            disk_id = int(item[2])
            block_address = int(item[4])
            counterstack.calculate_rd(disk_id, block_address)
            print line,
    counterstack.get_rd_values()

if __name__ == '__main__':
    main()
