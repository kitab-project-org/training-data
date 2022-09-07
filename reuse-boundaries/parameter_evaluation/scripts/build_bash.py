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

OVERWRITE = True # set to True if you want to overwrite existing csv files!

# BUILD LISTS OF PARAMETER RANGES: 
min_match_l = list(range(2, 11, 2))
min_align_l = list(range(30, 71, 10))
n_l = list(range(12, 37, 8))
gap_l = list(range(100, 801, 200))
n_gram_type = ["--floating-ngrams", ""]

# defaults:
max_df = 100
min_df = 2


# build path to the git repo and other paths:
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
print(root)

# script used to extract data from parquet files to csv:
to_csv_script = os.path.join(root, "reuse-boundaries/parameter_evaluation/scripts/1_align-stats_CM-WM_seriatim.py")


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
        with open(f+"/.dummy", mode="w") as file:
            file.write("")

# build list of the text pairs, based on the folder names of the manually evaluated texts:
text_pairs = []
##for folder in eval_folders:
##    for f in os.listdir(folder):
for f in os.listdir(input_folder):
    print(f)
    pth = os.path.join(input_folder, f)
    if os.path.isdir(pth):
        if f.startswith(exclude) or f.endswith(exclude):
            print("!! excluding", f, "!!")
        else:
            #print(f)
            
            text_pairs.append(f)
print(text_pairs)


# copy the passim input files to the input folder
original = "/home/admin-kitab/Documents/OpenITI/instantiations/2021/passim/Feb/pri"
if overwrite:
    print("input folder exists?", os.path.exists(input_folder))
    shutil.rmtree(input_folder)
    print("input folder exists after removing it?", os.path.exists(input_folder))
    for pair in text_pairs:
        textinfolder = os.path.join(input_folder, pair)
        os.makedirs(textinfolder)
        for fn in os.listdir(original):
            if fn.split("-")[0] in pair.split("_"):
                # copy json file to the appropriate input directory
                fp = os.path.join(original, fn)
                shutil.copyfile(fp, os.path.join(textinfolder, fn))
                

# build bash script file for each text pair:
for f in text_pairs:
    print("building bash scripts for", f)
    bash = []
    i = 0
    for mm, ma, gap, n, nt in product(min_match_l, min_align_l, gap_l, n_l, n_gram_type):
        #print(i, mm, ma, gap, n)
        if nt:
            outfolder_name =  f"{mm}_{ma}_{gap}_{n}_float_{f}"
        else:
            outfolder_name =  f"{mm}_{ma}_{gap}_{n}_nonfl_{f}"
        outfolder = os.path.join(output_folder, f, outfolder_name)
        csv_outfp = os.path.join(csv_folder, outfolder_name+".csv")
        if OVERWRITE or not os.path.exists(csv_outfp):
            #print(outfolder_name)
            i+=1
            
            # run passim (and time its execution):
            cmd =  f"time passim {input_folder}/{f} {outfolder} --pairwise --maxDF 100 "
            cmd += f"--min-match {mm} --min-align {ma} --gap {gap} -n {n} {nt}"
            #print(cmd)
            bash.append(cmd)
            
            # extract relevant data from passim output and create csv file:
            cmd =  f"time python3 {to_csv_script} {outfolder}/align.json {csv_folder}"
            bash.append(cmd)
            
            # remove raw passim output:
            bash.append(f"rm -rf {outfolder}")
            
            # push csv to GitHub:
            #bash.append(f"git add {csv_folder}")
            #bash.append(f"git commit -m 'ran passim {f} mm {mm} ma {ma} gap {gap} n {n}'")
            #bash.append("git pull origin master")
            #bash.append("git push origin master")
    
    with open(f"{bash_folder}/{f}.sh", mode="w", encoding="utf-8") as file:
        file.write("\n".join(bash))
    print(f"-> {i} passim runs written to bash script.")
