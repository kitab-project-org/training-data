"""
This script takes the initial passim outputs (pairwise or aggregated before) and adds character match (without counting
white spaces), char match percentage (using length of the aligned string), and word match to each alignment.
The output files will have the same structure as the passim outputs with four new columns:
    ch_match: character match without counting white spaces,
    align_len: length of the aligned string to be used in percentage value,
    matches_percentage: character match percentage using passim column "matches", which counts white spaces in
    char match, and 'align_len' column, which we produce above,
    w_match: word match

PV adapted the script to work with seriatim output (which has slightly 
different column names: series for series1, id for id1, uid for uid1, 
gid for gid1, begin for begin1, end for end1, seq for seq1)

seriatim output also lacks the following columns 
(partly because it does not use token offsets, only character offsets):
bw1, bw2, ew1, ew2, len1, len2, tok1, tok2, score

Example commands: 

By default, the token offsets will be calculated from the character offsets using a token-character ratio constant

`python3 1_align-stats_CM-WM_seriatim.py <passim_output_folder_align.json> <destination_folder_for_csv_documents>`

`python3 1_align-stats_CM-WM_seriatim.py ../../test/output/align.json ../../test/output/csv`

If you want to calculate the token-based columns on the real offsets of the tokens, provide the path 
to the folder containing the input documents and a path to where the token offsets should be stored:

`python3 1_align-stats_CM-WM_seriatim.py ../../test/output/align.json ../../test/output/csv ../../test/input/documents/ ../../test/resources/tok_offsets`
"""

from __future__ import print_function

import json
import math
import os
import pandas as pd
import re
import shutil
import sys

from bisect import bisect_left, bisect_right

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as F

tok_char_ratio = 0.19273941531214372 # tok_index = char_index * tok_char_ratio; ratio calculated from Arabic sample documents

def word_count(s1, s2):
    cnt = 0
    i = 0
    while i < len(s1):
        # print("i: ", i)
        prev_i = i
        while i < len(s1) and s1[i] != " ":
            i += 1
        if s1[prev_i:i] == s2[prev_i:i]:
            cnt += 1
        i += 1
    return cnt


def ch_count(s1, s2):
    cnt = 0
    for i in range(0, len(s1)):
        if s1[i] == s2[i] and all(s != " " for s in [s1[i], s2[i]]):
            cnt += 1
    return cnt


def match_per(match, length):
    if length == 0:
        return 0
    else:
        return (match/length) * 100

def list_end_of_token_offsets(s, token_regex="\w+"):
    """Generate a list of character offsets for the end of each token in s"""
    return [m.end() for m in re.finditer(token_regex, s)]


def char_to_tok(c, tok_offsets, begin=True):
    """Find the token offset based on a character offset

    Args:
        c (int): character offset
        tok_offsets (list): list of character offsets of the end of each token
        begin (bool): if True, the character offset is the beginning of a range

    Example:
        > s = "abc def ghi"
        > offsets = list_end_of_token_offsets(s)
        > for i in range(len(s)):
        >     print(i, s[i], ">", char_to_tok(i, offsets))
        0 a > 0
        1 b > 0
        2 c > 0
        3   > 0
        4 d > 1
        5 e > 1
        6 f > 1
        7   > 1
        8 g > 2
        9 h > 2
        10 i > 2
    """
    if begin:
        return bisect_left(tok_offsets, c)
    else:
        return bisect_right(tok_offsets, c)

def calc_token_offsets(in_folder, out_folder):
    """Generate lists of character offsets of the end of every token;
    one json file will be created for each text in in_folder,
    containing a dictionary (keys: milestone ids, values: list of offsets)

    Args:
        in_folder (str): path to the input folder; each file in that folder
            contains on every line a json document:
            "id": milestone id
            "text": normalized text of the milestone
        out_folder (str): path to folder where output json files will be stored
    """
    print("CALCULATING TOKEN OFFSETS")
    current_text_id = None
    d = dict()
    for fn in sorted(os.listdir(in_folder)):
        print("-", fn)
        text_id = fn.split("-")[0]
        if current_text_id and text_id != current_text_id:
            outfp = os.path.join(out_folder, current_text_id+".json")
            with open(outfp, mode="w", encoding="utf-8") as file:
                json.dump(d, file)
            d = dict()
        current_text_id = text_id
        fp = os.path.join(in_folder, fn)
        with open(fp, mode="r", encoding="utf-8") as file:
            docs = file.read().splitlines()
        for doc in docs:
            doc = json.loads(doc)
            ms_id = doc["id"].split(".")[-1]
            text = doc["text"]
            offsets = list_end_of_token_offsets(text)
            #if len(offsets) < 300:
            #    print(text_id, ms_id, len(offsets))
            d[ms_id] = offsets

    if d:
        outfp = os.path.join(out_folder, current_text_id+".json")
        with open(outfp, mode="w", encoding="utf-8") as file:
            json.dump(d, file)


def rearrange_cols_in_file(fp, outfp, offsets_folder):
    """Add some columns and rearrange their order so the format agrees with
    that of the csv files generated from normal passim runs.
    """
    df = pd.read_csv(fp, sep='\t')

    # load offset json files:
    fn = os.path.splitext(os.path.split(fp)[-1])[0]
    b1, b2 = fn.split("_")
    print("REARRANGING COLUMNS IN", fn)
    if offsets_folder: # create columns for token offsets based on the real character offsets of each token
        print("loading offset files from")
        b1_fp = os.path.join(offsets_folder, b1.split("-")[0]+".json")
        print("  ", b1_fp, os.path.exists(b1_fp))
        b2_fp = os.path.join(offsets_folder, b2.split("-")[0]+".json")
        print("  ", b2_fp, os.path.exists(b2_fp))
        with open(b1_fp, mode="r", encoding="utf-8") as file:
            b1_offsets = json.load(file)
        with open(b2_fp, mode="r", encoding="utf-8") as file:
            b2_offsets = json.load(file)
        print("b1_offsets loaded; number of items:", len(b1_offsets))
        print("b2_offsets loaded; number of items:", len(b2_offsets))

        # create token-based columns based on the offsets:
        df["bw1"] = df.apply(lambda row: char_to_tok(row.begin1, b1_offsets[row.id1.split(".")[-1]]), axis=1)
        df["bw2"] = df.apply(lambda row: char_to_tok(row.begin2, b2_offsets[row.id2.split(".")[-1]]), axis=1)
        df["ew1"] = df.apply(lambda row: char_to_tok(row.end1, b1_offsets[row.id1.split(".")[-1]], begin=False), axis=1)
        df["ew2"] = df.apply(lambda row: char_to_tok(row.end2, b2_offsets[row.id2.split(".")[-1]], begin=False), axis=1)
    else:  # create columns for token offsets based on a fixed token/character ratio
        df["bw1"] = df.apply(lambda row: math.floor(row.begin1 * tok_char_ratio), axis=1)
        df["bw2"] = df.apply(lambda row: math.floor(row.begin2 * tok_char_ratio), axis=1)
        df["ew1"] = df.apply(lambda row: min(300, math.ceil(row.end1 * tok_char_ratio)), axis=1)
        df["ew2"] = df.apply(lambda row: min(300, math.ceil(row.end2 * tok_char_ratio)), axis=1)
    #df["len1"] = df.apply(lambda row: row.end1 +1 - row.begin1, axis=1)
    #df["len2"] = df.apply(lambda row: row.end2 +1 - row.begin2, axis=1)
    df["len1"] = df.apply(lambda row: len(re.findall("\w", row.s1)), axis=1)
    df["len2"] = df.apply(lambda row: len(re.findall("\w", row.s2)), axis=1)
    df["score"] = df.apply(lambda row: (row.len1 + row.len2) / 2, axis=1)
    #df["tok1"] = df.apply(lambda row: row.ew1 + 1 - row.bw1, axis=1)
    #df["tok2"] = df.apply(lambda row: row.ew2 + 1 - row.bw2, axis=1)
    #df["tok1"] = df.apply(lambda row: len(re.findall("\w+", row.s1)), axis=1)
    #df["tok2"] = df.apply(lambda row: len(re.findall("\w+", row.s2)), axis=1)
    df["tok1"] = df.apply(lambda row: 300, axis=1)
    df["tok2"] = df.apply(lambda row: 300, axis=1)


    #cols = df.columns.tolist()
    #print(cols)

    # rearrange column order and drop superfluous columns:
    new_col_order = ['align_len', 'begin1', 'begin2', 'bw1', 'bw2',
                     'ch_match', 'end1', 'end2', 'ew1', 'ew2',
                     'gid1', 'gid2', 'id1', 'id2', 'len1', 'len2',
                     'matches', 'matches_percent',
                     's1', 's2', 'score',
                     'seq1', 'seq2', 'tok1', 'tok2',
                     'uid1', 'uid2', 'w_match', 'series_b1', 'series_b2', 'begin1']
    df = df[new_col_order]

    # rename columns:
    df = df.rename(columns={"begin1": "b1", "begin2": "b2",
                            "end1": "e1", "end2": "e2"})
    df.to_csv(outfp, sep="\t", index=False, encoding='utf-8-sig')


def rearrange_cols_in_folder(in_folder, out_folder, offsets_folder):
    for text_folder in os.listdir(in_folder):
        text_folder_path = os.path.join(in_folder, text_folder)
        if not os.path.isdir(text_folder_path):
            continue
        for fn in os.listdir(text_folder_path):
            fp = os.path.join(text_folder_path, fn)
            if not os.path.exists(os.path.join(out_folder, text_folder)):
                os.makedirs(os.path.join(out_folder, text_folder))
                print(os.path.join(out_folder, text_folder))
            outfp = os.path.join(out_folder, text_folder, fn)
            rearrange_cols_in_file(fp, outfp, offsets_folder)


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) not in (3, 5):
        print("Usage: align-stats_CM-WM_seriatim.py <passim_output_folder_align.json> <csv_output_folder>", file=sys.stderr)
        print("OR (slower but more exact token offsets): align-stats_CM-WM_seriatim.py <passim_output_folder_align.json> <csv_output_folder> <input_documents_folder> <token_offsets_folder>", file=sys.stderr)
        exit(-1)

    # calculate token offsets of the milestones in the input_documents_folder
    if len(sys.argv) == 5:
        token_offsets_folder = sys.argv[4]
        calc_token_offsets(sys.argv[3], sys.argv[4])
    else:
        print("Using token-character ratio constant", tok_char_ratio)
        token_offsets_folder = None

    # combine json/parquet files into csv files and add some statistics:

    # spark session
    # SparkSession.sparkContext.setLogLevel("All")
    spark = SparkSession.builder.appName('Stats').getOrCreate()

    word_match = F.udf(lambda s1, s2: word_count(s1, s2), IntegerType())
    ch_match = F.udf(lambda s1, s2: ch_count(s1, s2), IntegerType())
    match_percent = F.udf(lambda match, alig_len: match_per(match, alig_len), FloatType())
    align_len = F.udf(lambda s: len(s), IntegerType())

    # check the input format whether it is JSON or parquet
    in_file = sys.argv[1]
    if in_file.strip("/").endswith(".json"):
        file_type = "json"
    elif in_file.strip("/").endswith(".parquet"):
        file_type = "parquet"

    # define the matches_percent column
    ch_match_percent_col = F.when(F.col("align_len") == 0, 0.0)\
        .otherwise(match_percent('matches', 'align_len'))

    df = spark.read.format(file_type).options(encoding='UTF-8').load(in_file).distinct()
    print("here:")
    # df.printSchema()
    # drop rows that have null values in any column from passim outputs
    df = df.na.drop()
    dfGrouped = df.withColumn('ch_match', ch_match('s1', 's2')) \
        .withColumn('align_len', align_len('s1')) \
        .withColumn('matches_percent', ch_match_percent_col) \
        .withColumn('w_match', word_match('s1', 's2')) \
        .withColumn('series_b1', F.col('series')) \
        .withColumn('series_b2', F.col('series2')) \
        .withColumn('begin1', F.col('begin')) \
        .withColumn('end1', F.col('end')) \
        .withColumn('gid1', F.col('gid')) \
        .withColumn('id1', F.col('id')) \
        .withColumn('seq1', F.col('seq')) \
        .withColumn('uid1', F.col('uid')) \
        .repartition('series', 'series2') \
        .sortWithinPartitions('id', 'id2') \
        .write \
        .partitionBy('series', 'series2') \
        .format('csv') \
        .options(header='true', delimiter='\t') \
        .mode('overwrite') \
        .save(sys.argv[2])
    spark.stop()

    print("renaming starts!!!")
    for root, dirs, files in os.walk(sys.argv[2], topdown=False):
        if '/series2=' in root:
            print("root:", root)
            data_files = list(filter(lambda s: not s.startswith('.'), files))
            dot_files = list(filter(lambda s: s.startswith('.'), files))
            for dot_file in dot_files:
                os.remove(os.path.join(root, dot_file))
            if (len(data_files) > 0) and (data_files[0].startswith('part')):
                tmp1 = re.split("/series1?=", root)[1]
                tmp2 = tmp1.split("/series2=")
                b1 = tmp2[0]
                b2 = tmp2[1]
                # generate new filename and join it to the root path
                # new_f_name = b1 + "_" + b2 + '.csv.gz'
                new_f_name = b1 + "_" + b2 + '.csv'
                #new_f_name = b1 + "_" + b2 + '.json'
                new_f_path = os.path.join(root, new_f_name)
                # get the parent path of the root
                parent = os.path.abspath(os.path.join(root, os.pardir))
                # os.rename(os.path.join(root, rfiles[0]), re.sub('series2=', '', root) + '.json.gz')
                # rename the path of the file (root + old filename) to the path of parent dir (of root) + new filename.
                # E.g., changes /home/data/series1=JK001/series2=JK002/part.json.gz" to
                # "/home/data/series1=JK001/JK001_JK002.json.gz"
                os.rename(os.path.join(root, data_files[0]), os.path.join(parent, new_f_name))
            os.rmdir(root)
        elif '/series=' in root or '/series1=' in root:
            os.rename(root, re.sub('series1?=', '', root))

    # adapt csv files so that they have the same format as csv files created from regular passim outputs:
    rearrange_cols_in_folder(sys.argv[2], sys.argv[2], token_offsets_folder)





