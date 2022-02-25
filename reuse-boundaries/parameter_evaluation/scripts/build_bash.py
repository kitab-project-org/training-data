"""Build a bash script for each text pair that
will run passim with all permutations of a set of parameters,
extract the relevant data from each run in a csv file,
remove the raw passim data, and push the csv file to GitHub

Include only bash scripts for each text pair + parameters for which no csv file exists in output folder!

NB: csv files are stored in the output/csv folder, and have file names like this:
GVDB20200120_LMN20200820_3_7_25_3.csv
(BK1_BK2_MINMATCH_MINALIGN_GAP_N.csv)

TO DO:
* after json files were added to the `input` folder,
  use the content of the input folder as the source for the text_pairs list.
* insert Mathew's script for extracting the relevant data from parquet files.
  (make sure the script takes as input the relevant align.json folder
  and the output folder where it should write the csv file;
  the csv filename should follow this pattern: BK1_BK2_MINMATCH_MINALIGN_GAP_N.csv)
"""

from itertools import product

import os

OVERWRITE = False # set to True if you want to overwrite existing csv files!

# BUILD LISTS OF PARAMETER RANGES: 
min_match_l = list(range(3,11, 1))
min_align_l = list(range(7, 25, 1))
n_l = list(range(3, 7, 1))
gap_l = list(range(25, 201, 25))

# script used to extract data from parquet files to csv:
to_csv_script = "scripts/1_align-stats_CM-WM_seriatim.py" # TO DO: replace with Mathew's script

# build path to the git repo and other paths:
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#print(root)

# folders to be evaluated:
folder1 = os.path.join(root, r"reuse-boundaries/Evaluation-Hackathon/Evaluation-Hackathon-Marked")
folder2 = os.path.join(root, r"reuse-boundaries/Evaluated")
eval_folders = [folder1, folder2]
exclude = ("JK000001", )  # text pairs starting with these text ids will be left out of selection

# build paths to relevant folders:
output_folder = os.path.join(root, r"reuse-boundaries/parameter_evaluation/output")
csv_folder = os.path.join(output_folder, "csv")
input_folder = os.path.join(root, r"reuse-boundaries/parameter_evaluation/input")
bash_folder = os.path.join(root, r"reuse-boundaries/parameter_evaluation/bash_scripts")
for f in [output_folder, csv_folder, input_folder, bash_folder]:
    if not os.path.exists(f):
        os.makedirs(f)

# build list of the text pairs, based on the folder names of the manually evaluated texts:
text_pairs = []
for folder in eval_folders:
    for f in os.listdir(folder):
        if f.startswith(exclude):
            print("!! excluding", f, "!!")
        else:
            #print(f)
            pth = os.path.join(folder, f)
            if os.path.isdir(pth):
                text_pairs.append(f)

# build bash script file for each text pair:
for f in text_pairs:
    print("building bash scripts for", f)
    bash = []
    i = 0
    for mm, ma, gap, n in product(min_match_l, min_align_l, gap_l, n_l):
        #print(i, mm, ma, gap, n)
        outfolder_name =  f"{f}_{mm}_{ma}_{gap}_{n}"
        outfolder = os.path.join(output_folder, f, outfolder_name)
        csv_outfp = os.path.join(csv_folder, outfolder_name+".csv")
        if OVERWRITE or not os.path.exists(csv_outfp):
            i+=1
            
            # run passim:
            cmd =  f"passim {input_folder}/{f} {outfolder} --pairwise --maxDF 100 "
            cmd += f"--min-match {mm} --min-align {ma} --gap {gap} -n {n}"
            #print(cmd)
            bash.append(cmd)
            
            # extract relevant data from passim output and create csv file:
            cmd =  f"python3 {to_csv_script} {outfolder}/align.json {csv_folder}"
            bash.append(cmd)
            
            # remove raw passim output:
            bash.append(f"rm -rf {outfolder}")
            
            # push csv to GitHub:
            bash.append(f"git add {csv_folder}")
            bash.append(f"git commit -m 'ran passim {f} mm {mm} ma {ma} gap {gap} n {n}'")
            bash.append("git pull origin master")
            bash.append("git push origin master")
            
    with open(f"{bash_folder}/{f}.sh", mode="w", encoding="utf-8") as file:
        file.write("\n".join(bash))
    print(f"-> {i} passim runs written to bash script.")

