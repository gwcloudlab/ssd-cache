#!/bin/bash
python MRtoMSRformat.py sort_long_b4096.trace
cat sort_long_b4096.csv hm.csv  > combined.csv
sort -n combined.csv > hm_msr_all.csv
grep -nr 848627760 hm_msr_all.csv
head -n 1435807 hm_msr_all.csv > hm_msr_pruned.csv
