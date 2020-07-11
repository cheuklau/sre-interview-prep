# Write a program that reads in two csv files:
#
# $ cat dataset1.csv
# NAME,LEG_LENGTH,DIET
# Hadrosaurus,1.2,herbivore
# Struthiomius,0.92,omnivore
# Velociraptor,1.0,carnivore
# Triceratops,0.87,herbivore
# Euplocephalus,1.6,herbivore
# Stegosaurus,1.40,herbivore
# Tyrannosaurus Rex,2.5,carnivore
#
# $ cat dataset2.csv
# NAME,STRIDE_LENGTH,STANCE
# Euoplocephalus,1.87,quadrupedal
# Stegosaurus,1.90,quadrupedal
# Tyrannosaurus Rex,5.76,bipedal
# Hadrosaurus,1.4,bipedal
# Deinonychus,1.21,bipedal
# Struthimimus,1.34,bipedal
# Velociraptor,2.72,bipedal
#
# Then prints the names of bipedal dinosaurs from
# fastest to slowest.
#
# Speed is given by
# ((STRIDE_LENGTH / LEG_LENGTH) - 1) * SQRT(LEG_LENGTH * g)
#
# Strategy:
# We need to combine information from both
# datasets in order to calculate the speed.
# We read in the first dataset to form a dictionary
# with dinosaur name and leg length as value.
# Next, we read in the second dataset and
# for each row if the stance is bipedal
# we calculate the speed.
# We can store the speed as the key and
# the name of the dinosaur as the value in
# a dictonary.
# we can also store the speed in a separate
# array sort it, then use the sorted array to get
# the values in the dictionary to print.
#
# Key idea
# Use csv library DictReader to read in a csv file.
# Each item in the DictReader object contains
# a row of the csv file mapped to the header.
#

import csv
import math

# Read in the first dataset
leg_length = {}
with open('dataset1.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        leg_length[row['NAME']] = row['LEG_LENGTH']

# Read in the second dataset
speed_dict = {}
speed_arry = []
with open('dataset2.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['STANCE'] == 'bipedal' and row['NAME'] in leg_length:
            tmp = (float(row['STRIDE_LENGTH'])/float(leg_length[row['NAME']])-1.0)*math.sqrt(float(leg_length[row['NAME']])*9.81)
            speed_dict[str(tmp)] = row['NAME']
            speed_arry.append(tmp)

speed_arry.sort()
for speed in speed_arry:
    print speed_dict[str(speed)]


