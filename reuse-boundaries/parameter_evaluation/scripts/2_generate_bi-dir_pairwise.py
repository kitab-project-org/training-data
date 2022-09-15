import gzip
import io
import os
import csv
import re

if __name__ == '__main__':
    # uni_dir_path = input("Enter the path to the uni-dir data: ")
    # bi_dir_path = input("Enter the path to write the new files: ")

    headers = ["uid2", "uid", "gid", "gid2", "begin", "end", "begin2", "end2", "_corrupt_record", "id", "seq",
               "_corrupt_record2", "id2", "seq2", "s1", "s2", "matches", "ch_match", "align_len", "matches_percent",
               "w_match", "series_b1", "series_b2"]
    start_folder = "/home/admin-kitab/Documents/passim/passim-seriatim/parameter_eval/training-data/reuse-boundaries/parameter_evaluation/output/csv"
    for uni_dir_fn in os.listdir(start_folder):
        print("***"*20)
        print("RUN:", uni_dir_fn)
        print("***"*20)

        uni_dir_path =  os.path.join(start_folder, uni_dir_fn)
        for root, dirs, files in os.walk(uni_dir_path):
            dirs[:] = [d for d in dirs]
            # path before the book1 dir, e.g., /home/admin/data/
            rfiles = filter(lambda s: not s.startswith(('.', '_')), files)
            for file in rfiles:
                print(file)
                #root_dir = root.rsplit("/", 1)[0]
                root_dir = os.path.dirname(root)
                # print("root: ", root)
                # print("file: ", file)
                file_name_parts = file.split("_")
                b1 = file_name_parts[0]
                try:
                    b2 = re.sub(".csv(.gz)?", "", file_name_parts[1])  # remove the extension
                except:
                    continue
                # New file path and name for the other direction of data
                # new_file_name = b2 + "_" + b1 + ".csv.gz"
                new_file_name = b2 + "_" + b1 + ".csv"
                new_file_dir = os.path.join(root_dir, b2)
                print("new: ", new_file_dir)
                # create the new dir and file for the other direction of data
                os.makedirs(new_file_dir, exist_ok=True)
                # with gzip.open(os.path.join(root, file), "rt", encoding='utf8') as uni_dir_file:
                with open(os.path.join(root, file), "r", encoding='utf-8') as uni_dir_file:
                    uni_dir_data = csv.DictReader(uni_dir_file, delimiter='\t')
                    dh = dict((h, h) for h in uni_dir_data.fieldnames)
                    # with gzip.open(os.path.join(new_file_dir, new_file_name), "w") as new_file:
                    with open(os.path.join(new_file_dir, new_file_name), "w", encoding="utf-8") as new_file:
                        # with io.TextIOWrapper(new_file, encoding='utf-8') as wrapper:
                        #     writer = csv.DictWriter(wrapper, headers, delimiter='\t')
                        writer = csv.DictWriter(new_file, fieldnames=uni_dir_data.fieldnames, delimiter='\t')
                        writer.writeheader()
                        for u_data in uni_dir_data:
                            try:
                                writer.writerow({"uid2": u_data["uid"], "uid": u_data["uid2"],
                                                 "gid": u_data["gid2"], "gid2": u_data["gid"],
                                                 "begin": u_data["begin2"], "end": u_data["end2"],
                                                 "begin2": u_data["begin"], "end2": u_data["end"],
                                                 "id": u_data["id2"], "id2": u_data["id"],
                                                 "seq2": u_data["seq"], "seq": u_data["seq2"],
                                                 #"_corrupt_record": u_data["_corrupt_record2"],
                                                 #"_corrupt_record2": u_data["_corrupt_record"],
                                                 "s1": u_data["s2"], "s2": u_data["s1"],
                                                 "matches": u_data["matches"],
                                                 "ch_match": u_data["ch_match"], "align_len": u_data["align_len"],
                                                 "matches_percent": u_data["matches_percent"], "w_match": u_data["w_match"],
                                                 "series_b1": u_data["series_b2"], "series_b2": u_data["series_b1"]})
                            except:
                                writer.writerow({"uid2": u_data["uid1"], "uid1": u_data["uid2"],
                                                 "gid1": u_data["gid2"],  "gid2": u_data["gid1"],
                                                 "b1": u_data["b2"], "e1": u_data["e2"],
                                                 "bw1": u_data["bw2"], "ew1": u_data["ew2"],
                                                 "b2": u_data["b1"], "e2": u_data["e1"],
                                                 "bw2": u_data["bw1"], "ew2": u_data["ew1"],
                                                 "id1": u_data["id2"], "id2": u_data["id1"], 
                                                 "seq1": u_data["seq2"], "seq2": u_data["seq1"],
                                                 "s1": u_data["s2"], "s2": u_data["s1"],
                                                 "first1": u_data["first2"], "first2": u_data["first1"],
                                                 "len1": u_data["len2"], "len2": u_data["len1"],
                                                 "tok1": u_data["tok2"], "tok2": u_data["tok1"],
                                                 "matches": u_data["matches"],
                                                 "score": u_data["score"],
                                                 "ch_match": u_data["ch_match"],
                                                 "align_len": u_data["align_len"],
                                                 "matches_percent": u_data["matches_percent"],
                                                 "w_match": u_data["w_match"],
                                                 "series_b1": u_data["series_b2"], "series_b2": u_data["series_b1"]})


#begin	begin2	end	end2	gid	gid2	id	id2	matches	s1	s2	seq	seq2	uid	uid2	bw1	ew1	bw2	ew2	ch_match	align_len	matches_percent	w_match	series_b1	series_b2
