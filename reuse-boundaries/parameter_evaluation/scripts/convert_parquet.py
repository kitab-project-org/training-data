# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 09:28:26 2022

@author: mathe
"""

import pyarrow.parquet as pq
import pandas as pd
import os
import sys

def parquet_to_csv(parquet_path):
    """Take a directory containing parquet files for a book pair. Convert those parquet files to 
    csv files, save the csv file under the name of the directory and delete the input directory
    """
    df_out = pd.DataFrame()
    csv_name = parquet_path + ".csv"
    for root, dirs, files in os.walk(parquet_path, topdown=False):
        for name in files:
            pq_path = os.path.join(root, name)            
            df = pq.read_table(pq_path).to_pandas()
            df_out = pd.concat([df_out, df])
    df_out.to_csv(csv_name, encoding='utf-8-sig', index = False)

# Fetch the first argument passed to the script and use that as the script path
parquet_path = sys.argv[1]

parquet_to_csv(parquet_path)