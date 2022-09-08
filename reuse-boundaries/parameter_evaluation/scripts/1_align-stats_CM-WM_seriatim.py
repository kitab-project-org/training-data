"""
This script takes the initial passim outputs (pairwise or aggregated before) and adds character match (without counting
white spaces), char match percentage (using length of the aligned string), and word match to each alignment.
The output files will have the same structure as the passim outputs with four new columns:
    ch_match: character match without counting white spaces,
    align_len: length of the aligned string to be used in percentage value,
    matches_percentage: character match percentage using passim column "matches", which counts white spaces in
    char match, and 'align_len' column, which we produce above,
    w_match: word match
"""

from __future__ import print_function

import os
import re
import shutil
import sys

import findspark
findspark.init()


from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as F


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


def get_tok_pos(ms, ms_txt, local_ch_offset):
    local_tok_offset = 0

    for i in ms_txt[:local_ch_offset]:
        if i == ' ':
            local_tok_offset = local_tok_offset + 1
    tok_offset = ((int(ms) - 1) * 300) + int(local_tok_offset)
    return tok_offset



if __name__ == '__main__':
    print(sys.argv)
    if not os.path.exists(sys.argv[1]):
        print("passim did not produce output. Saving empty csv file")
        text_pair = os.path.basename(os.path.dirname(os.path.dirname(sys.argv[1])))
        t1 = text_pair.split("_")[0]
        header = "begin\tbegin2\tend\tend2\tgid\tgid2\tid\tid2\tmatches\ts1\ts2\tseq\tseq2\tuid\tuid2\tbw1\tew1\tbw2\tew2\tch_match\talign_len\tmatches_percent\tw_match\tseries_b1\tseries_b2\n"
        os.makedirs(os.path.join(sys.argv[2], t1))
        with open(os.path.join(sys.argv[2], t1, text_pair+".csv"), mode="w", encoding="utf-8") as file:
            file.write(header)
        sys.exit()
    # if len(sys.argv) != 2:
    #     print("Usage: align-stats_CM-WM.py <input> <output>", file=sys.stderr)
    #     exit(-1)
    # spark session
    # SparkSession.sparkContext.setLogLevel("All")
    spark = SparkSession.builder.appName('Stats').getOrCreate()

    word_match = F.udf(lambda s1, s2: word_count(s1, s2), IntegerType())
    ch_match = F.udf(lambda s1, s2: ch_count(s1, s2), IntegerType())
    match_percent = F.udf(lambda match, alig_len: match_per(match, alig_len), FloatType())
    align_len = F.udf(lambda s: len(s), IntegerType())
    tok_pos = F.udf(lambda ms, ms_text, local_ch_pos: get_tok_pos(ms, ms_text, local_ch_pos))

    # check the input format whether it is JSON or parquet
    in_file = sys.argv[1]
    print("in file: ", in_file)
    if in_file.strip("/").endswith(".json"):
        file_type = "json"
    elif in_file.strip("/").endswith(".parquet"):
        file_type = "parquet"
    print("f type: ", file_type)

    # define the matches_percent column
    ch_match_percent_col = F.when(F.col("align_len") == 0, 0.0)\
        .otherwise(match_percent('matches', 'align_len'))

    df = spark.read.format(file_type).options(encoding='UTF-8').load(in_file).distinct()
      
   # drop rows that has null values in any column from passim outputs
   # df = df.na.drop()
    dfGrouped = df.withColumn('bw1', tok_pos('seq', 's1', 'begin')) \
        .withColumn('ew1', tok_pos('seq', 's1', 'end')) \
        .withColumn('bw2', tok_pos('seq2', 's2', 'begin2')) \
        .withColumn('ew2', tok_pos('seq2', 's2', 'end2')) \
        .withColumn('ch_match', ch_match('s1', 's2')) \
        .withColumn('align_len', align_len('s1')) \
        .withColumn('matches_percent', ch_match_percent_col) \
        .withColumn('w_match', word_match('s1', 's2')) \
        .withColumn('series_b1', F.col('series')) \
        .withColumn('series_b2', F.col('series2'))
    df_g2 = dfGrouped \
        .repartition('series', 'series2') \
        .sortWithinPartitions('id', 'id2')# \
    df_g2 \
        .write \
        .partitionBy('series', 'series2') \
        .format('csv') \
        .options(header='true', delimiter='\t') \
        .mode('overwrite') \
        .save(sys.argv[2])
    spark.stop()

#    print("renaming starts!!!")
    for root, dirs, files in os.walk(sys.argv[2], topdown=False):
        print("root: ", root)
        if '/series2=' in root:
            data_files = list(filter(lambda s: not s.startswith('.'), files))
            dot_files = list(filter(lambda s: s.startswith('.'), files))
            for dot_file in dot_files:
                os.remove(os.path.join(root, dot_file))
            if (len(data_files) > 0) and (data_files[0].startswith('part')):
                tmp1 = root.split("/series=")[1]
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
        elif '/series=' in root:
            os.rename(root, re.sub('series=', '', root))





