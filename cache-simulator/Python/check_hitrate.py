import os
import sys
import csv
import math


filename = sys.argv[1]
output_filename = "file"

with open(os.path.join("MSR", output_filename), "wb") as wr:
    with open(os.path.join("MSR", filename), "rb") as trace:
        for item in csv.reader(trace, delimiter=','):
            block_address = int(item[4])
            read_size = int(item[5])
            blocks = int(math.ceil(read_size / 4096.0))
            for block in xrange(blocks):
                if block > 0:
                    block_address += 1
                wr.write(str(block_address) + '\n')

os.system("sort -u MSR/file > MSR/unique")
file_lines = sum(1 for line in open('MSR/file'))
unique_lines = sum(1 for line in open('MSR/unique'))
print "No. of blocks:\t\t", file_lines
print "No. of unique_blocks:\t", unique_lines
print "No. of hits:\t\t", file_lines - unique_lines
print "Hit rate:\t\t", (file_lines - unique_lines)/float(file_lines) * 100
