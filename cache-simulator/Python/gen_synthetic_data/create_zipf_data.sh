#!/bin/sh
fio --debug=time,io --output-format=json --eta-newline=time --output=fio_read.out zipf.fio
grep -oh "off=[0-9]*/len=[0-9]*" fio_read.out > sample
grep -oh "[0-9]\{8\}\|[0-9]\{9\}\|[0-9]\{10\}" sample > zipf.data
rm sample
python convert_to_msr_format.py
