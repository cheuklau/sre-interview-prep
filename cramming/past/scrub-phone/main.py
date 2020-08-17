#!/usr/bin/env python

import re

# This task is probably too simple to use a Python script for.
# A single sed command is sufficient.

infile = open("phone.orig", "r")
outfile = open("phone.new", "w")
for line in infile:
	outfile.write(re.sub(r'\d{3}-\d{3}-\d{4}', 'XXX-XXX-XXXX', line))