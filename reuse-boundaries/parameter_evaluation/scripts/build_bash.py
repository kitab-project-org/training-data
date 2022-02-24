from itertools import product

import os

os.path.realpath
input_folders = []
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
print(root)

folder1 = os.path.join(root, r"reuse-boundaries/Evaluation-Hackathon/Evaluation-Hackathon-Marked")
folder2 = os.path.join(root, r"reuse-boundaries/Evaluated")
for folder in [folder1, folder2]:
    for f in os.listdir(folder):
        pth = os.path.join(folder, f)
        if os.path.isdir(pth):
            input_folders.append(f)

min_match_l = list(range(3,11, 1))
min_align_l = list(range(7, 25, 1))
n_l = list(range(3, 7, 1))
gap_l = list(range(25, 201, 25))


output_folder = os.path.join(root, r"reuse-boundaries/parameter_evaluation/output")
input_folder = os.path.join(root, r"reuse-boundaries/parameter_evaluation/input")
bash_folder = os.path.join(root, r"reuse-boundaries/parameter_evaluation/bash_scripts")
print(bash_folder)


to_csv_script = "1_align-stats_CM-WM_seriatim.py" # replace with Mathew's script

for f in input_folders:
    print(f)
    bash = []
    i = 0
    for mm, ma, gap, n in product(min_match_l, min_align_l, gap_l, n_l):
        #print(i, mm, ma, gap, n)
        #input()
        i+=1
        outfolder = f"{output_folder}/{f}/{f}_{mm}_{ma}_{gap}_{n}"
        cmd =  f"passim {input_folder}/{f} {outfolder} --pairwise --maxDF 100 "
        cmd += f"--min-match {mm} --min-align {ma} -- gap {gap} -n {n}"
        #print(cmd)
        bash.append(cmd)
        cmd =  f"python3 {to_csv_script} {outfolder}/align.json output/csv"
        bash.append(cmd)
        bash.append(f"rm -rf {outfolder}")
        bash.append("git add output/csv")
        bash.append(f"git commit -m 'ran passim mm {mm} ma {ma} gap {gap} n {n}'")
        bash.append("git push origin master")
    with open(f"{bash_folder}/{f}.sh", mode="w", encoding="utf-8") as file:
        file.write("\n".join(bash))
    

