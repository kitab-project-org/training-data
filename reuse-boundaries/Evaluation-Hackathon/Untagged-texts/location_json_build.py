# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 13:32:59 2021

@author: mathe
"""

import json
import pandas as pd

in_csv = "C:/Users/mathe/Documents/Kitab QNL/Github repos/training-data/reuse-boundaries/Evaluation-Hackathon/Untagged-texts/Text-pairs.csv"
out_loc = "C:/Users/mathe/Documents/Kitab QNL/Github repos/training-data/reuse-boundaries/Evaluation-Hackathon/Evaluated-texts/hackathon-locations.json"

def json_loc (in_csv, out_loc):
    listed = pd.read_csv(in_csv).values.tolist()
    with open(out_loc, 'a') as out:
        
        for row in listed:
            json_row = {}
            json_row["b1"] = row[0]
            json_row["b2"] = row[1]
            json_row["annotator"] = row[2]
            json_row["lines_evaluated_b1"] = []
            json_row["lines_evaluated_b2"] = []
            json_row["comments"] = ""
        
        
    
            json.dump(json_row, out, indent = 1)
    


json_loc(in_csv, out_loc)