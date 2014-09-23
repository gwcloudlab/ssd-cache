import os
import csv

WINDOWS_TICK = 10000000
SEC_TO_UNIX_EPOCH = 11644473600


def WindowsTickToUnixSeconds(windowsTicks):
    return (windowsTicks / WINDOWS_TICK - SEC_TO_UNIX_EPOCH)

with open(os.path.join("traces/MSR-Cambridge-2/proj", "pre-processed.csv"), "wb") as wr:
    sentinal = 0
    writr = csv.writer(wr, delimiter=',')
    with open(os.path.join("traces/MSR-Cambridge-2/proj", "sorted.csv"), "rb") as trace:
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
            writr.writerow([time_of_access, hostname, disk_id, operation, block_address, read_size, response_time])
