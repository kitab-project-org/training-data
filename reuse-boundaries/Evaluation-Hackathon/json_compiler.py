# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 16:19:20 2021

@author: mathe
"""

import json
import os

jsons_path = "C:/Users/mathe/Documents/Kitab QNL/Github repos/training-data/reuse-boundaries/Evaluation-Hackathon/Evaluated-texts/Jsons"

new_json = "C:/Users/mathe/Documents/Kitab QNL/Github repos/training-data/reuse-boundaries/Evaluation-Hackathon/Evaluated-texts/hackathon-locations.json"

os.chdir(jsons_path)

listed = []

for root, dirs, files in os.walk(".", topdown=False):
    for file in files:
        json_path = os.path.join(root, file)
        print(json_path)
        with open(json_path) as j:
            data = json.load(j)
            j.close()
            listed.append(data)


json = json.dumps(listed, indent=1)

with open(new_json, 'w') as o:
    o.write(json)
    o.close()



