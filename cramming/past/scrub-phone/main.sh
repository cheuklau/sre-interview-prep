#!/bin/bash

# Method 1
# Here we do a grep with
# -E to denote extended regex
# -o to denote we only want to output matches in a newline
# Read in the file called phone.orig
#
# The output will be each phone number in a newline
# This will be piped into xargs with
# -I{} replace occurrences of {} with the phone numbers piped
# in from grep one at a time
#
# xargs is wrapped around sed with
# -i '' indicates we want to replace in-place on the file
# Note that the empty quotes '' is only required on MacOS to indicate
# we do not want a backup copy of the original.
#
# The extra copies and moves allows us to keep the original file.
# cp phone.orig phone.tmp
# grep -Eo '\d{3}-\d{3}-\d{4}' phone.orig | xargs -I{} sed -i '' 's/{}/XXX-XXX-XXXX/g' phone.orig
# mv phone.orig phone.new
# mv phone.tmp phone.orig

# Method 2
# Here we use the regex directly in sed but sadly regex in sed is a bit iffy.
# For example, we had to use [[:digit:]] (or [0-9]) instead of \d and
# we have to specify -E for sed to understand extended regular expressions.
# For GNU instead of -E we use -r.
#
# The extra copies and moves allows us to keep the original file.
cp phone.orig phone.tmp
sed -i '' -E 's/[[:digit:]]{3}-[[:digit:]]{3}-[[:digit:]]{4}/XXX-XXX-XXXX/g' phone.orig
mv phone.orig phone.new
mv phone.tmp phone.orig