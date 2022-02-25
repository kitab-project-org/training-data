# -*- coding: utf-8 -*-
"""
Script to read get ms numbers based on line ranges for texts
"""

import json
import re
import pandas as pd
import os

def get_ms_for_lines(texts_folder, eval_jsons, out_csv):
    """Function that takes a folder of pairs of texts split into folders
    and a json file containing addresses for each folder and the texts within.
    It takes the text, splits them into lines, isolates the lines specified in
    the json and then finds the first and last milestones within that line range.
    The text and the first and last milestones are outputted to a csv."""
    
    out_list = []
    
    with open(eval_jsons) as f:
        listed_evals = json.load(f)
        f.close()
    
    for evaluation in listed_evals:
        bid1 = evaluation["text_1"] 
        bid2 = evaluation["text_2"]
        text_dir = texts_folder + "/" + bid1 + "_" + bid2 + "/"
        print(text_dir)
        # Open the first text, read in the lines and find the milestone ranges
        with open(text_dir + bid1, encoding = "utf-8") as f:
            split_text = f.read().splitlines()
            f.close()
        
        
        for line_range in evaluation["taggedSections_1"]:
            subset = split_text[line_range[0]: line_range[1]]
            for line in subset:
                milestone = re.search(r"ms\d+\s", line)                
                if milestone:                    
                    first_ms = int(milestone.group(0)[2:])
                    break
            for line in reversed(subset):
                milestone = re.search(r"ms\d+\s", line)
                if milestone:
                    last_ms = int(milestone.group(0)[2:])
                    break
        
            out_list.append([bid1, first_ms, last_ms])
        
        # Open second text and read in the lines and find the milestone ranges
        with open(text_dir + bid2, encoding = "utf-8") as f:
            split_text = f.read().splitlines()
            f.close()
        
        
        for line_range in evaluation["taggedSections_2"]:
            subset = split_text[line_range[0]:line_range[1]]
            for line in subset:
                milestone = re.search(r"ms\d+\s", line)
                if milestone:
                    first_ms = int(milestone.group(0)[2:])
                    break
            for line in reversed(subset):
                milestone = re.search(r"ms\d+\s", line)
                if milestone:
                    last_ms = int(milestone.group(0)[2:])
                    break
        
            out_list.append([bid2, first_ms, last_ms])
    
    out_df = pd.DataFrame(out_list, columns = ["bid", "firstMs", "lastMs"])
    out_df = out_df.drop_duplicates()
    out_df.to_csv(out_csv, index = False)
    
text_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/tagged_texts/"
json_path = text_path + "hackathon-locations-for-eval.json"
out_path = text_path + "id_ms_list.csv"

get_ms_for_lines(text_path, json_path, out_path)
    
    
    ### Write script to loop through parquet files using pyarrow and concat into one df