# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 17:23:38 2022

@author: mathe
"""

import os
import re
path = "C:/Users/mathe/Documents/Github-repos/training-data/reuse-boundaries/parameter_evaluation/tagged_texts"

os.chdir(path)
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if re.search(r"-ara1", name):
            full_path = os.path.join(root, name)
            new_name = name.split("-")[0].split(".")[-1]
            new_path = os.path.join(root, new_name)
            os.rename(full_path, new_path)
            