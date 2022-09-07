# this does not work yet: imech files do not have only the ID as filename, but also -arax.extension

import os
import requests

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
imech_folder = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "input")
bash_folder = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "bash_scripts")
ms_csv_fp = os.path.join(root, "reuse-boundaries", "parameter_evaluation", "tagged_texts", "id_ms_list.csv")
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
print(text_pairs)
#base_url = "https://github.com/OpenITI/i.mech/raw/master/data/"
base_url = "https://raw.githubusercontent.com/OpenITI/i.mech/master/data/"


for pair in text_pairs:
    for bk in pair.split("_"):
        outfolder = os.path.join(imech_folder, pair)
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        for i in range(1, 100):
            url = base_url+bk+"-{:05d}".format(i*300)
            print(url)
            outfp = os.path.join(outfolder, bk+"-{:05d}".format(i*300))
##            try:
##                if not os.path.exists(outfp):
##                    with requests.get(url, stream=True) as r:
##                        with open(outfp, mode="wb") as f:
##                            for chunk in r.iter_content(chunk_size=8192):
##                                f.write(chunk)
##            except: # last batch reached
##                break
