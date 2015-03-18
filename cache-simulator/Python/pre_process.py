import os
import sys
import csv

WINDOWS_TICK = 10000000
SEC_TO_UNIX_EPOCH = 11644473600


def WindowsTickToUnixSeconds(windowsTicks):
    return (windowsTicks / WINDOWS_TICK - SEC_TO_UNIX_EPOCH)

for arg in sys.argv[1:]:
    filename = arg
    print filename
    name, ext = filename.split('.')
    output_filename = name + "_sorted." + ext

    with open(os.path.join("MSR", output_filename), "wb") as wr:
        sentinal = 0
        writr = csv.writer(wr, delimiter=',')
        with open(os.path.join("MSR", filename), "rb") as trace:
            for item in csv.reader(trace, delimiter=','):
                if sentinal == 0:
                    sentinal = WindowsTickToUnixSeconds(int(item[0]))
                time_of_access = WindowsTickToUnixSeconds(int(item[0])) - sentinal
                hostname = item[1]
                disk_id = int(item[2])
                operation = item[3]
                block_address = item[4]
                read_size = int(item[5])
                response_time = int(item[6])
                if operation == "Read":
                    writr.writerow([time_of_access, hostname, disk_id, operation, block_address, read_size, response_time])
