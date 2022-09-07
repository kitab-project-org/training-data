import os
import re
import json


# build path to the git repo and other paths:
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#print(root)

# folders to be evaluated:
folder1 = os.path.join(root, r"reuse-boundaries/Evaluation-Hackathon/Evaluation-Hackathon-Marked")
folder2 = os.path.join(root, r"reuse-boundaries/Evaluated")
eval_folders = [folder1, folder2]
exclude = ("JK000001", )  # text pairs starting with these text ids will be left out of selection

# build paths to relevant folders:
output_folder = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "output")
csv_folder = os.path.join(output_folder, "csv")
input_folder = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "input")
bash_folder = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "bash_scripts")
ms_csv_fp = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "tagged_texts", "id_ms_list.csv")
for f in [output_folder, csv_folder, input_folder, bash_folder]:
    if not os.path.exists(f):
        os.makedirs(f)

def build_ms_d(csv_fp):
    """Build a dictionary of all the milestones that were evaluated for each book pair"""
    with open(csv_fp, mode="r", encoding="utf-8") as file:
        data = file.read().splitlines()
    header = data.pop(0)
    ms_d = dict()
    for row in data:
        bk, first_ms, last_ms = row.split(",")
        if not bk in ms_d:
            ms_d[bk] = []
        ms_d[bk] += list(range(first_ms, last_ms+1))
    # convert milestones to string:
    return {k: [str(int(x)) for x in v] for k,v in ms_d.items()}
        

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

i_mech_folder = r"../i.mech"

##ms_d = {
##    "GVDB20200120": [1,5, 50, 80],
##    "LMN20200820": [2,4, 8, 10]
##    }
##
##ms_d_new = {k: [str(int(x)) for x in v] for k,v in ms_d.items()}
##ms_d = ms_d_new
ms_d = build_ms_d(ms_csv_fp)

row_d = {k: [] for k in ms_d}

for f, ms in ms_d.items():
    for fn in os.listdir(i_mech_folder):
        if f in fn:
            print(fn)
            fp = os.path.join(i_mech_folder, fn)
            with open(fp, mode="r", encoding="utf-8") as file:
                for row in file.readlines():
                    if re.findall(f"^ms(?:{'|'.join(ms)})\t", row):
                        row_d[f].append(row)
#print(json.dumps(row_d, ensure_ascii=False, indent=2))

for f in text_pairs:
    infolder = os.path.join(input_folder, f)
    for bk in f.split("_"):
        fp = os.path.join(infolder, bk)
        if bk in row_d:
            if not os.path.exists(infolder):
                os.makedirs(infolder)
            with open(fp, mode='w', encoding="utf-8") as file:
                file.write("".join(row_d[bk]))
        
    
            
