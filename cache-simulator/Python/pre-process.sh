#!/bin/sh

# Run within the MSR/ dir. Run as MSR/pre-process.sh
if [ -z "$1" ]
then
  echo "Provide a relative directory as input"
  exit 1
fi

working_dir=$1
working_dir="`pwd`/$1"
folderName=$(basename $working_dir)
cd $working_dir
echo $folderName
cat *.csv | parallel --pipe grep ",Read," > combined.csv
# cat combined.csv | parallel --pipe grep ",Read," > combined_read_only.csv
sort -n combined.csv > "$folderName"_reads_only.csv
rm combined.csv
mv "$folderName"_reads_only.csv ../
