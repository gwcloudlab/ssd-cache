#!/bin/bash

cd MSR/
tar xf msr-cambridge1.tar
tar xf msr-cambridge2.tar

cd MSR-Cambridge/
gunzip *.gz

# For all files except txt files
for FILE in `ls -p -I '*.txt' | grep -v /`
do
    curr_file="${FILE%_*}"
    mkdir -p $curr_file
    mv "$curr_file"_*.csv $curr_file
done | uniq

echo "If you get an error like mv: cannot stat ‘hm_*.csv’: No such file or directory please igonre"
echo "Need regex fix"

for dir in */
do
    echo "Processing $dir"
    cd $dir
    folderName=$(basename $dir)
    cat *.csv | parallel --no-notice --pipe grep ",Read," > combined.csv
    sort -n combined.csv > "$folderName".csv
    rm combined.csv
    mv "$folderName".csv ../../
    cd ../
done                        
