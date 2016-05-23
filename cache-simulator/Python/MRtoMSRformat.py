"""
This file converts the output from mapreduce to MSR format
"""
import sys
import csv

for arg in sys.argv[1:]:
    filename = arg
    print filename
    name, ext = filename.split('.')
    output_filename = name + ".csv"

with open(output_filename, "wb") as wr:
    writr = csv.writer(wr, delimiter=',')
    with open(filename, "rb") as trace:
        for item in csv.reader(trace, delimiter=" "):
            time_of_access = int(float(item[0]))
            block_address = int(item[1])
            read_size = int(item[2])
            hostname = "mr"
            disk_id = 5  # Should we change this???
            operation = "Read"
            response_time = 0
            writr.writerow([time_of_access, hostname, disk_id, operation, block_address, read_size, response_time])
