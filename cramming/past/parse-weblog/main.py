#!/usr/bin/env python

import re
import collections

webfile = "webserver.log"

# Create regex object with the same expression as bash script.
# Note that we are grouping the entire IP and nothing else.
re_obj = re.compile(r'(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

# Go through each line of the webfile.
# Use the re match method on each line.
# If there is a match then get the IP and increment the count
# for that IP in a counter object.
# Note that counter is preferred over a dict here because we need
# to return the top 10 at the end and there is no way to
# sort a dict.
result = collections.Counter()
infile = open(webfile, "r")
for line in infile:
	match = re_obj.match(line)
	if match:
		ip_tmp = match.groups()[0]
		result[ip_tmp] += 1
for ip, pings in result.most_common(10):
	print '%4s %s' % (pings, ip)
