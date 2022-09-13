"""
Compare the outputs of the parameter test runs with the old passim output.


"""

import os
import re
import json
from csv import DictReader
import statistics



test_header = "begin	begin2	end	end2	gid	gid2	id	id2	"
test_header += "matches	s1	s2	seq	seq2	uid	uid2"
test_header += "bw1	ew1	bw2	ew2	ch_match	align_len	"
test_header += "matches_percent	w_match	series_b1	series_b2"
test_header = test_header.split("\t")

test_pairs = [
    'GVDB20200120_LMN20200820'
    'JK000911_JK001330'
    'JK001259-ara1_Shamela0002864-ara1'
    #'Shamela0005880_Shamela0009783'
    'Shamela0005880_Shamela0009783BK1'
    'Shamela0011680_Shamela0011780'
    'Shamela19Y0145334_Shamela0000176'
    'Shia001131Vols_EShia0071536'
    ]

def get_overlap(b_old, e_old, b_new, e_new):
    """Check whether the old and new spans overlap.

    If there is no overlap: return False
    If there is overlap, return a tuple (begin_difference, end_difference)

    OVERLAP CASES:

           b_old       e_old
    b_new        e_new

           b_old       e_old
                 b_new        e_new

           b_old       e_old
    b_new                    e_new

           b_old                    e_old
                 b_new        e_new

    NON_OVERLAP CASES:

        b_old       e_old
                             b_new        e_new
                             
                             b_old       e_old
    b_new        e_new
    """
    if int(b_new) > int(e_old) or int(b_old) > int(e_new):
        return False
    else:
        return (int(b_new)-int(b_old), int(e_new)-int(e_old))

def make_row_id(row, old_or_new):
    """Create a unique ID for the alignment"""
    if old_or_new == "new":
        return "new_{}_b{:04d}_e{:04d}_{}_b{:04d}_e{:04d}".format(row["id"], int(row["begin"]), int(row["end"]),
                                                                  row["id2"], int(row["begin2"]), int(row["end2"]))
    else:
        return "old_{}_b{:04d}_e{:04d}_{}_b{:04d}_e{:04d}".format(row["id1"], int(row["b1"]), int(row["e1"]),
                                                                  row["id2"], int(row["b2"]), int(row["e2"]))

def get_relevant_srt_data(srt_fp, cols):
    """Create a dictionary from the relevant columns from the srt data
    key: milestone in book1
    val: list of dictionaries (json representation of the selected columns
                               for each row that contains this milestone)
    """
    data = []
    with open(srt_fp, mode="r", encoding="utf-8") as file:
        srt_reader = DictReader(file, delimiter="\t")
        for row in srt_reader:
            data.append({k: row[k] for k in cols})
            
    # sort by milestone:
    ms_data = dict()
    for row in data:
        try:
            ms1 = row["id1"].split(".")[-1]
        except:
            ms1 = row["id"].split(".")[-1]
        if ms1 not in ms_data:
            ms_data[ms1] = []
        ms_data[ms1].append(row)
    return ms_data


def log_overlap(b1_or_b2, start_or_end, overlap, old_row_id, new_row_id,
                ignore_offsets, stats, d):
    """
    Store the overlap in the stats dictionary,
    and details in the d[etailed_stats] dictionar

    Args:
        b1_or_b2 (str): "B1" or "B2" (for "Book1" and "Book2"
        start_or_end (str): "start" or "end"
        overlap (int): the difference between the end or start offsets of an alignment
        old_row_id (str): ID of the alignment in the old run
        new_row_id (str): ID of the alignment in the new run
        ignore_offsets (list): list of row ids of which the difference
            in offsets should not be recorded (because they are part
            of either split or conjoined alignments)
        stats (dict): a dictionary containing the summary statistics
            of the differences between the two runs
        d (dict): a dictionary containing the detailed statistics
            of the differences between the two runs
    """
    if old_row_id in ignore_offsets or new_row_id in ignore_offsets:
        return
    
    if overlap == 0:
        k = start_or_end+"_did_not_change"
        stats[k] += 1
        d[k] + 1
    elif overlap > 0:
        k = start_or_end+"s_later_in_new"
        stats[k] += 1
        fmt = "{}: alignment {}s {} characters later in new run"
        stmt = fmt.format(b1_or_b2, start_or_end, overlap)
        d[k].append((stmt, old_row_id, new_row_id))
    else:
        k = start_or_end+"s_earlier_in_new"
        stats[k] += 1
        fmt = "{}: alignment {}s {} characters earlier in new run"
        stmt = fmt.format(b1_or_b2, start_or_end, -overlap)
        d[k].append((stmt, old_row_id, new_row_id))
    k = "all_{}_differences".format(start_or_end)
    stats[k].append(overlap)

        
def find_srt_changes(old_srt_fp, new_srt_fp, stats, detailed_stats,
                     old_cols=["id1", "b1", "e1", "id2", "b2", "e2", "uid1", "uid2"],
                     new_cols=["id", "begin", "end", "id2", "begin2", "end2", "uid", "uid2"]):
    """
    Get stats on the differences between 2 srt files of the same text pair
    """
    print("find_srt_changes")
    print("get relevant OLD columns:", old_srt_fp)
    old_data = get_relevant_srt_data(old_srt_fp, old_cols)
    
    print("get relevant NEW columns:", new_srt_fp)
    new_data = get_relevant_srt_data(new_srt_fp, new_cols)
    
    d = {
        "alignments_in_old": sum([len(old_data[ms]) for ms in old_data]),
        "alignments_in_new": sum([len(new_data[ms]) for ms in new_data]),
        "not_in_old": [],
        "not_in_new": [],
        "starts_earlier_in_new": [],
        "starts_later_in_new": [],
        "ends_earlier_in_new": [],
        "ends_later_in_new": [],
        "split_in_new": [],
        "combined_in_new": [],
        "start_did_not_change": 0,
        "end_did_not_change": 0
    }
    stats["alignments_in_old_total"] += d["alignments_in_old"]
    stats["alignments_in_new_total"] += d["alignments_in_new"]

    ignore_offsets = [] # row IDs that are part of a split or join

    for ms1 in old_data:
        if ms1 not in new_data:
            for old_row in old_data[ms1]:
                stats["not_in_new"] += 1
                old_row_id = make_row_id(old_row, "old")
                d["not_in_new"].append(old_row_id)
        else:
            for i, old_row in enumerate(old_data[ms1]):
                old_row_id = make_row_id(old_row, "old")
                overlapping_new_rows = dict()
                for j, new_row in enumerate(sorted(new_data[ms1], key=lambda row: int(row["begin"]))):
                    if new_row["id2"] == old_row["id2"]:
                        new_row_id = make_row_id(new_row, "new")
                        B1_overlap = get_overlap(old_row["b1"], old_row["e1"],
                                                 new_row["begin"], new_row["end"])
                        B2_overlap = get_overlap(old_row["b2"], old_row["e2"],
                                                 new_row["begin2"], new_row["end2"])
                        if B1_overlap and B2_overlap:
                            #overlapping_old_rows[j] = (B1_overlap, B2_overlap)
                            #overlapping_old_rows[j] = (B1_overlap, B2_overlap, old_row_id, new_row_id)
                            overlapping_new_rows[j] = {"overlap B1 (start,end)": B1_overlap,
                                                       "overlap B2 (start,end)": B2_overlap,
                                                       "new row": new_row,
                                                       "new row ID": new_row_id}
                if len(overlapping_new_rows) > 1:
                    stats["split_in_new"] += 1
                    #d["combined_in_new"].append(new_row["id"])
                    d["split_in_new"].append({"old row": old_row_id,
                                              "overlapping new rows": overlapping_new_rows})
                    
                    # compute the difference with the old alignment
                    # and the start of the first split fragment
                    # and the end of the last split fragment:
                    
                    #first_new_row = sorted(new_data[ms1], key=lambda row: int(row["begin"]))[0]
                    first_new_row_index = min(overlapping_new_rows.keys())
                    first_new_row = overlapping_new_rows[first_new_row_index]["new row"]
                    B1_overlap = get_overlap(old_row["b1"], old_row["e1"],
                                             first_new_row["begin"], first_new_row["end"])
                    B2_overlap = get_overlap(old_row["b2"], old_row["e2"],
                                             first_new_row["begin2"], first_new_row["end2"])
                    new_row_id = make_row_id(first_new_row, "new")
                    log_overlap("B1", "start", B1_overlap[0], old_row_id, new_row_id, ignore_offsets, stats, d)
                    log_overlap("B2", "start", B2_overlap[0], old_row_id, new_row_id, ignore_offsets, stats, d)

                    #last_new_row = sorted(new_data[ms1], key=lambda row: int(row["begin"]))[-1]
                    last_new_row_index = max(overlapping_new_rows.keys())
                    last_new_row = overlapping_new_rows[last_new_row_index]["new row"]
                    B1_overlap = get_overlap(old_row["b1"], old_row["e1"],
                                             last_new_row["begin"], last_new_row["end"])
                    B2_overlap = get_overlap(old_row["b2"], old_row["e2"],
                                             last_new_row["begin2"], last_new_row["end2"])
                    new_row_id = make_row_id(last_new_row, "new")
                    log_overlap("B1", "end", B1_overlap[0], old_row_id, new_row_id, ignore_offsets, stats, d)
                    log_overlap("B2", "end", B2_overlap[0], old_row_id, new_row_id, ignore_offsets, stats, d)

                    # make sure the offset difference of split alignments is not counted again:
                    ignore_offsets.append(old_row_id)
                    for k in overlapping_new_rows:
                        ignore_offsets.append(overlapping_new_rows[k]["new row ID"])

    for ms1 in new_data:
        if ms1 not in old_data:
            for new_row in new_data[ms1]:
                row_id = make_row_id(new_row, "new")
                stats["not_in_old"] += 1
                d["not_in_old"].append(row_id)
##        elif len(new_data[ms1]) > len(old_data[ms1]):
##            stats["split_in_new"] += len(new_data[ms1]) - len(old_data[ms1]
##            d["split_in_new"].append(row["uid"])
##        elif len(new_data[ms1]) < len(old_data[ms1]):
##            stats["combined_in_new"] += len(old_data[ms1] - len(new_data[ms1])
##            d["combined_in_new"].append(row["uid"])
        else:
##            if len(new_data[ms1]) > len(old_data[ms1]):
##                stats["split_in_new"] += len(new_data[ms1]) - len(old_data[ms1])
##                d["split_in_new"].append(ms1)

            for i, new_row in enumerate(new_data[ms1]):
                new_row_id = make_row_id(new_row, "new")
                overlapping_old_rows = dict()
                for j, old_row in enumerate(sorted(old_data[ms1], key=lambda row: int(row["b1"]))):
                    #old_row = old_data[ms1][j]
                    old_row_id = make_row_id(old_row, "old")
                    if new_row["id2"] == old_row["id2"]:  # this must always be True, because id = version id + milestone number?!
                        B1_overlap = get_overlap(old_row["b1"], old_row["e1"],
                                                 new_row["begin"], new_row["end"])
                        B2_overlap = get_overlap(old_row["b2"], old_row["e2"],
                                                 new_row["begin2"], new_row["end2"])
##                        if old_row_id.startswith("old_Shia001131Vols-ara1.completed.ms173_b0433"):
##                            print("---")
##                            print(i, new_row_id)
##                            print(j, old_row_id)
##                            print("B1_overlap:", B1_overlap)
##                            print("B2_overlap:", B2_overlap)
                        if B1_overlap and B2_overlap:
                            #overlapping_old_rows[j] = (B1_overlap, B2_overlap)
                            #overlapping_old_rows[j] = (B1_overlap, B2_overlap, old_row_id, new_row_id)
                            overlapping_old_rows[j] = {"overlap B1 (start,end)": B1_overlap,
                                                       "overlap B2 (start,end)": B2_overlap,
                                                       "old row": old_row,
                                                       "old row ID": old_row_id}
                            if old_row_id.startswith("old_Shia001131Vols-ara1.completed.ms173_b0433"):
                                print(overlapping_old_rows)
                        
                if len(overlapping_old_rows) == 0:
                    stats["not_in_old"] += 1
                    d["not_in_old"].append(new_row_id)
                elif len(overlapping_old_rows) > 1:
                    stats["combined_in_new"] += 1
                    #d["combined_in_new"].append(new_row["id"])
                    overlapping_old_row_ids = [overlapping_old_rows[j]["old row ID"] for j in overlapping_old_rows]
                    d["combined_in_new"].append({"new row": new_row_id,
                                                 "overlapping old rows": overlapping_old_row_ids})

                    # compute the difference with the new alignment
                    # and the start of the first combined fragment
                    # and the end of the last combined fragment:
                    
                    first_old_row_index = min(overlapping_old_rows.keys())
                    first_old_row = overlapping_old_rows[first_old_row_index]["old row"]
                    B1_overlap = get_overlap(new_row["begin"], new_row["end"],
                                             first_old_row["b1"], first_old_row["e1"])
                    B2_overlap = get_overlap(new_row["begin2"], new_row["end2"],
                                             first_old_row["b2"], first_old_row["e2"])
                    old_row_id = make_row_id(first_old_row, "old")
                    log_overlap("B1", "start", B1_overlap[0], new_row_id, old_row_id, ignore_offsets, stats, d)
                    log_overlap("B2", "start", B2_overlap[0], new_row_id, old_row_id, ignore_offsets, stats, d)

                    last_old_row_index = max(overlapping_old_rows.keys())
                    last_old_row = overlapping_old_rows[last_old_row_index]["old row"]
                    B1_overlap = get_overlap(new_row["begin"], new_row["end"],
                                             last_old_row["b1"], last_old_row["e1"])
                    B2_overlap = get_overlap(new_row["begin2"], new_row["end2"],
                                             last_old_row["b2"], last_old_row["e2"])
                    old_row_id = make_row_id(last_old_row, "old")
                    log_overlap("B1", "end", B1_overlap[0], new_row_id, old_row_id, ignore_offsets, stats, d)
                    log_overlap("B2", "end", B2_overlap[0], new_row_id, old_row_id, ignore_offsets, stats, d)

                    # make sure the offset difference of split alignments is not counted again:
                    ignore_offsets.append(new_row_id)
                    for k in overlapping_old_rows:
                        ignore_offsets.append(overlapping_old_rows[k]["old row ID"])
                elif len(overlapping_old_rows) == 1:
                    j = list(overlapping_old_rows.keys())[0]
                    old_row_id = overlapping_old_rows[j]["old row ID"]
                    #print("overlapping_old_rows:", overlapping_old_rows)
                    #B1_start_overlap = overlapping_old_rows[j][0][0]

                    B1_start_overlap = overlapping_old_rows[j]["overlap B1 (start,end)"][0]
                    log_overlap("B1", "start", B1_start_overlap, old_row_id, new_row_id, ignore_offsets, stats, d)

                    B1_end_overlap = overlapping_old_rows[j]["overlap B1 (start,end)"][1]
                    log_overlap("B1", "end", B1_end_overlap, old_row_id, new_row_id, ignore_offsets, stats, d)
                    
                    B2_start_overlap = overlapping_old_rows[j]["overlap B2 (start,end)"][0]
                    log_overlap("B2", "start", B2_start_overlap, old_row_id, new_row_id, ignore_offsets, stats, d)
                    
                    B2_end_overlap = overlapping_old_rows[j]["overlap B2 (start,end)"][1]
                    log_overlap("B2", "end", B2_end_overlap, old_row_id, new_row_id, ignore_offsets, stats, d)
                
    fn = old_srt_fp.split("/")[-1][:-4]
    detailed_stats[fn] = d



##def find_csv(run_folder, b1, b2, rev=False):
##    fn = None
##    for b1_f in os.listdir(run_folder):
##        if b1 in b1_f:
##            for f in os.listdir(os.path.join(run_folder, b1)):
##                if b2 in f:
##                    fn = f
##                    break
##    if fn:
##        return fn
##    else:
##        if rev:
##            return None
##        else:
##            return find_csv(run_folder, b2, b1, rev=True)

def find_csv(run_folder, b1, b2, rev=False):
    """
    Find the csv file that contains the output for b1 and b2 pair
    """
    for f in os.listdir(os.path.join(run_folder, b1)):
        if b2 in f:
            return f

def json2tsv(d):
    """
    Convert the stats dictionary to a csv file
    """
    tsv = []
    for run in d:
        row = [run,]
        headers = sorted(list(d[run].keys()))
        for h in headers:
            row.append(str(d[run][h]))
        tsv.append("\t".join(row))
    header = "run\t" + "\t".join(headers)
    return header + "\n" + "\n".join(tsv)

def calculate_averages(all_stats):
    for k, stats in all_stats.items():
        print(k)
        stats["average_start_difference"] = sum(stats["all_start_differences"]) / len(stats["all_start_differences"])
        stats["average_end_difference"] = sum(stats["all_end_differences"]) / len(stats["all_end_differences"])
        stats["median_start_difference"] = statistics.median(stats["all_start_differences"])
        stats["median_end_difference"] = statistics.median(stats["all_end_differences"])
        stats["max_start_difference"] = max(stats["all_start_differences"])
        stats["max_end_difference"] = max(stats["all_end_differences"])
        stats["min_start_difference"] = min(stats["all_start_differences"])
        stats["min_end_difference"] = min(stats["all_end_differences"])
        
        del stats["all_start_differences"]
        del stats["all_end_differences"]
    

def main(test_csv_folder="ouput/csv", old_csv_folder="2021_1_4_outputs",
         stats_folder="stats"):
    """
    Compare the ouputs from the test runs with the old passim output
    and store statistics.
    """
    all_stats = dict()
    
    if not os.path.exists(stats_folder):
        os.makedirs(stats_folder)
    detailed_stats_folder = os.path.join(stats_folder, "detailed")
    if not os.path.exists(detailed_stats_folder):
        os.makedirs(detailed_stats_folder)

    for run in os.listdir(test_csv_folder):
        run_folder = os.path.join(test_csv_folder, run)
        if not os.path.isdir(run_folder):
            continue
        print(run)
        stats = {
            "alignments_in_old_total": 0,
            "alignments_in_new_total": 0,
            "not_in_old": 0,
            "not_in_new": 0,
            "starts_earlier_in_new": 0,
            "starts_later_in_new": 0,
            "start_did_not_change": 0,
            "ends_earlier_in_new": 0,
            "ends_later_in_new": 0,
            "end_did_not_change": 0,
            "all_start_differences": [],
            "all_end_differences": [],
            "split_in_new": 0,
            "combined_in_new": 0
            }
        detailed_stats = dict()
        
        for old_output_fn in os.listdir(old_csv_folder):
            old_output_fp = os.path.join(old_csv_folder, old_output_fn)
            b1, b2 = old_output_fn.split(".csv")[0].split("_")
            test_csv_fn = find_csv(run_folder, b1, b2, rev=False)
            if test_csv_fn:
                test_csv_fp = os.path.join(run_folder, b1, test_csv_fn)
                find_srt_changes(old_output_fp, test_csv_fp, stats, detailed_stats)
            else:
                print(run, ": no output found for", old_output_fn)
        all_stats[run] = stats
        outfp = os.path.join(detailed_stats_folder, run+".json")
        with open(outfp, mode="w", encoding="utf-8") as file:
            json.dump(detailed_stats, file, ensure_ascii=False,
                      indent=4, sort_keys=True)
    print("keys in all_stats:", list(all_stats.keys()))
    with open(os.path.join(stats_folder, "all_stats.json"), mode="w", encoding="utf-8") as file:
        json.dump(all_stats, file, ensure_ascii=False, indent=2, sort_keys=True)
    calculate_averages(all_stats)
    tsv = json2tsv(all_stats)
    with open(os.path.join(stats_folder, "all_stats.tsv"), mode="w", encoding="utf-8") as file:
        file.write(tsv)


root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(root)

test_csv_folder = os.path.join(root, "output", "csv")
old_csv_folder = os.path.join(root, "2021_1_4_outputs")
stats_folder = os.path.join(root, "stats")
main(test_csv_folder, old_csv_folder, stats_folder)

