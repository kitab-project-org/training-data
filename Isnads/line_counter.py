# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 10:16:43 2020

@author: mathe
"""

# This script is written to work with the json files in the training data repo. 
# It will count the number of lines tagged per text, flag if any text has lines above 5000 and below 0.
# As the json files are not using separators uniformly (sometimes ',' or '-') this searches for values
# using regex rather than a package for reading jsons 

import re

data = open("C:/Users/mathe/Documents/Kitab QNL/Github repos/training-data/Isnads/isnadTaggedLocations.json", encoding='utf-8')
line_ranges = re.findall('"taggedSections":(.+),"full', data.read())
data.close()

per_text_diff = []
total_line = 0
text_no = 0
error_list = []

# Extracting line numbers from json and counting differences - accounting for errors in the separation notation using regex
for pairs in line_ranges:
    n1 = re.findall(r'(\d+)[,-]', pairs)    
    n2 = re.findall(r'[,-](\d+)', pairs)    
    per_text_count = 0
    text_no = text_no + 1    
    for idx, n in enumerate(n1):
        diff = int(n2[idx]) - int(n) - 1
        per_text_count = diff + per_text_count
    per_text_diff.append(per_text_count)
    total_line = total_line + per_text_count
    # Doing an error check for numbers that appear to be outliers
    if per_text_count >= 5000 or per_text_count <= 0:
        error_list.append("| approx line no: " + str(text_no) + " | list of pairs : " + pairs + " | total: " + str(per_text_count) +" | ")    
    
# Printing results to console
print("number of lines per text:" + str(per_text_diff))
print()
print()
try: 
    print("check errors in json!: ")
    for error in error_list:
        print(str(error))
except IndexError:
    print("no errors found in json")
print()
print()    
print("total lines evaluated:" + str(total_line))
    
        

