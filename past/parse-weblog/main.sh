#!/bin/bash

# Grep options:
# -E is for extended regex which gives you full regex capability
# -o is for printing only the matched string with each match on a separate line
#
# Next we sort the results so the same IPs are next to each other
# Next we run uniq -c which gets the count of each unique IP
# Next we sort by count in reverse order so that the greatest count is first
# Finally we return the top 10 results
grep -Eo "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" webserver.log | sort | uniq -c | sort -r | head -10
