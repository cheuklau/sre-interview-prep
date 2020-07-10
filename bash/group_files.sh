#!/bin/bash

# Find all txt files in folder
files=(`find . -type f | grep txt`)

# Initialize results with first file
results=(${files[0]})

# Go through remaining files
for file in ${files[@]:1}
do
  # Go through each set of results
  idx=0
  match=0
  for result in ${results[@]}
  do
    # If they match then add to the result
    tmp=`echo $result | cut -d ';' -f 1`
    result=`cmp $file $tmp`
    if [ $? == 0 ]; then
       results[$idx]+=";$file"
       match=1
    fi
    let idx+=1
  done
  if [ $match == 0 ]; then
    results+=($file)
  fi
done

for result in ${results[@]}
do
  echo $result
done
