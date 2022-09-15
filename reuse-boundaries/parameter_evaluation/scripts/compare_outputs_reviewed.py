"""
Compare the outputs of the parameter test runs with the old passim output
BUT ONLY FOR THE MANUALLY REVIEWED PARTS OF THE TEXT PAIRS!
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
    -------------------------------------------------
    b_old        e_old
           b_new          e_new
    -------------------------------------------------
           b_old       e_old
    b_new                    e_new
    -------------------------------------------------
    b_old                    e_old
           b_new       e_new


    NON_OVERLAP CASES:

    b_old       e_old
                             b_new        e_new
    -------------------------------------------------
                             b_old       e_old
    b_new        e_new

    Args:
        b_old (str): the offset of the beginning of the alignment in the old srt file
        e_old (str): the offset of the end of the alignment in the old srt file
        b_new (str): the offset of the beginning of the alignment in the new srt file
        e_new (str): the offset of the end of the alignment in the new srt file
    """
    if int(b_new) > int(e_old) or int(b_old) > int(e_new):
        return False
    else:
        return (int(b_new)-int(b_old), int(e_new)-int(e_old))

def make_row_id(row, old_or_new):
    """Create a unique ID for the alignment

    Args:
        row (dict): a dictionary representation of a row in the srt file
        old_or_new (str): either "old" or "new"
    """
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
    Store the overlap between two alignments in the stats dictionary,
    and details in the d[etailed_stats] dictionary

    Args:
        b1_or_b2 (str): either "B1" or "B2" (for "Book1" and "Book2")
        start_or_end (str): either "start" or "end"
        overlap (int): the difference between the end or start offsets of an alignment 
            in the old and new runs as calculated by the get_overlap function
            (always new offset minus old offset)
        old_row_id (str): ID of the alignment in the old run (created by the make_row_id function)
        new_row_id (str): ID of the alignment in the new run (created by the make_row_id function)
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
    #d["evaluated_alignments_in_old"].append(old_row_id)
    #stats["evaluated_alignments_in_old"] += 1
    #d["evaluated_alignments_in_new"].append(new_row_id)
    #stats["evaluated_alignments_in_new"] += 1


def log_evaluated_alignments(old_or_new, b1, b2, id_ms_d, srt_data, stats, d):
    for ms1, alignments in srt_data.items():
        for alignment in alignments:
             ms2 = alignment["id2"]
             row_id = make_row_id(alignment, old_or_new)
             if was_ms_evaluated(b1, ms1, id_ms_d) and was_ms_evaluated(b2, ms2, id_ms_d):
                 stats["evaluated_alignments_in_"+old_or_new] += 1
                 d["evaluated_alignments_in_"+old_or_new].append(row_id)


def was_ms_evaluated(b, ms, id_ms_d):
    """
    Check whether a milestone falls within the list of evaluated milestone ranges

    Args:
        b (str): book ID 
        ms (str): milestone ID (<bookID>.ms<msID>)
        id_ms_d (dict): key: book IDs, values: list of tuples (start, end) of evaluated milestone ranges within that book
    """
    if b not in id_ms_d:
        print(b, "not among evaluated books!")
        return False
    evaluated_ranges = id_ms_d[b]
    ms_no = int(re.findall("\d+", ms)[-1])
    for start, end in evaluated_ranges:
        if start <= ms_no <= end:
            print("ms", ms_no, "of", b, "was evaluated")
            return True
    #print("milestone", ms, "of", b, "was not evaluated")
    return False

def find_srt_changes(old_srt_fp, new_srt_fp, b1, b2, stats, detailed_stats, id_ms_d,
                     old_cols=["id1", "b1", "e1", "id2", "b2", "e2", "uid1", "uid2"],
                     new_cols=["id", "begin", "end", "id2", "begin2", "end2", "uid", "uid2"]):
    """
    Get stats on the differences between 2 srt files of the same text pair

    Args:
        old_srt_fp (str): path to the srt file from the old run
        new_srt_fp (str): path to the srt file from the new run
        stats (dict): a dictionary containing the summary statistics
            of the differences between the two runs
        detailed_stats (dict): a dictionary containing the detailed statistics
            of the differences between the two runs
        old_cols (list): list of the column headers of the relevant columns in the old run
        new_cols (list): list of the column headers of the relevant columns in the new run
    """
    # Get the relevant columns from the srt files in dictionary format
    # (key: milestone, value: list of dictionaries, one for each alignment in that milestone)

    #print("get relevant OLD columns:", old_srt_fp)
    old_data = get_relevant_srt_data(old_srt_fp, old_cols)

    #print("get relevant NEW columns:", new_srt_fp)
    new_data = get_relevant_srt_data(new_srt_fp, new_cols)

    b1 = b1.split("-")[0]
    b2 = b2.split("-")[0]

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
        "end_did_not_change": 0,
        "evaluated_alignments_in_old": [],
        "evaluated_alignments_in_new": []
    }
    stats["alignments_in_old_total"] += d["alignments_in_old"]
    stats["alignments_in_new_total"] += d["alignments_in_new"]

    log_evaluated_alignments("old", b1, b2, id_ms_d, old_data, stats, d)
    log_evaluated_alignments("new", b1, b2, id_ms_d, new_data, stats, d)



    ignore_offsets = [] # row IDs that are part of a split or join

    # start from the old_data side: identify alignments that are not in the new run,
    # and those alignments that got split into multiple shorter alignments in the new run: 

    for ms1 in old_data:
        # do not check alignments in milestones that were not evaluated:
        if id_ms_d:
            if not was_ms_evaluated(b1, ms1, id_ms_d):
                continue

        if ms1 not in new_data:
            for old_row in old_data[ms1]:
                stats["not_in_new"] += 1
                old_row_id = make_row_id(old_row, "old")
                d["not_in_new"].append(old_row_id)
                #d["evaluated_alignments_in_old"].append(old_row_id)
                #stats["evaluated_alignments_in_old"] += 1
        else:
            for i, old_row in enumerate(old_data[ms1]):
                old_row_id = make_row_id(old_row, "old")
                overlapping_new_rows = dict()
                for j, new_row in enumerate(sorted(new_data[ms1], key=lambda row: int(row["begin"]))):
                    if new_row["id2"] == old_row["id2"]:
                        # do not check alignments in milestones that were not evaluated:
                        ms2 = new_row["id2"]
                        if id_ms_d:
                            if not was_ms_evaluated(b2, ms2, id_ms_d):
                                continue

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
                    #d["evaluated_alignments_in_old"].append(old_row_id)
                    #stats["evaluated_alignments_in_old"] += 1
                    #for j, r in overlapping_new_rows.items():
                    #    d["evaluated_alignments_in_new"].append(r["new row ID"])
                    #    stats["evaluated_alignments_in_new"] += 1

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

                else:
                    pass # we'll deal with those from the new_data side!

    # deal with the other situations: identify alignments that were not in the old run,
    # shorter alignments in the old run that got combined into one longer alignment in the new run,
    # and alignments that do overlap in the old and new runs:

    for ms1 in new_data:
        # do not check alignments in milestones that were not evaluated:
        if id_ms_d:
            if not was_ms_evaluated(b1, ms1, id_ms_d):
                continue

        if ms1 not in old_data:
            for new_row in new_data[ms1]:
                row_id = make_row_id(new_row, "new")
                stats["not_in_old"] += 1
                d["not_in_old"].append(row_id)
                #d["evaluated_alignments_in_new"].append(row_id)
                #stats["evaluated_alignments_in_new"] += 1

        else:
            for i, new_row in enumerate(new_data[ms1]):
                new_row_id = make_row_id(new_row, "new")
                overlapping_old_rows = dict()
                for j, old_row in enumerate(sorted(old_data[ms1], key=lambda row: int(row["b1"]))):
                    #old_row = old_data[ms1][j]
                    old_row_id = make_row_id(old_row, "old")
                    if new_row["id2"] == old_row["id2"]:  # this must always be True, because id = version id + milestone number?!
                        # do not check alignments in milestones that were not evaluated:
                        ms2 = new_row["id2"]
                        if id_ms_d:
                            if not was_ms_evaluated(b2, ms2, id_ms_d):
                                continue

                        B1_overlap = get_overlap(old_row["b1"], old_row["e1"],
                                                 new_row["begin"], new_row["end"])
                        B2_overlap = get_overlap(old_row["b2"], old_row["e2"],
                                                 new_row["begin2"], new_row["end2"])
                        if B1_overlap and B2_overlap:
                            overlapping_old_rows[j] = {"overlap B1 (start,end)": B1_overlap,
                                                       "overlap B2 (start,end)": B2_overlap,
                                                       "old row": old_row,
                                                       "old row ID": old_row_id}

                if len(overlapping_old_rows) == 0:
                    stats["not_in_old"] += 1
                    d["not_in_old"].append(new_row_id)
                    #d["evaluated_alignments_in_new"].append(new_row_id)
                    #stats["evaluated_alignments_in_new"] += 1


                elif len(overlapping_old_rows) > 1:
                    stats["combined_in_new"] += 1
                    overlapping_old_row_ids = [overlapping_old_rows[j]["old row ID"] for j in overlapping_old_rows]
                    d["combined_in_new"].append({"new row": new_row_id,
                                                 "overlapping old rows": overlapping_old_row_ids})
                    #d["evaluated_alignments_in_new"].append(new_row_id)
                    #stats["evaluated_alignments_in_new"] += 1
                    #for r in overlapping_old_row_ids:
                    #    d["evaluated_alignments_in_old"].append(r)
                    #    stats["evaluated_alignments_in_old"] += 1


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

                    # make sure the offset difference of combined alignments is not counted again later:
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
    if not id_ms_d:
        del d["evaluated_alignments_in_old"]
        del d["evaluated_alignments_in_new"]
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
    Find the csv file that contains the output for b1 and b2 pair in the current run

    Returns the filename of the csv file (or None if it was not found)
    """
    try:
        for f in os.listdir(os.path.join(run_folder, b1)):
            if b2 in f:
                return f
    except:
        print("folder not found:", os.path.join(run_folder, b1))

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
    """
    Calculate some statistics on the differences of start and end offsets between two runs.
    """
    for run, stats in all_stats.items():
        #print("calculating averages for", run)
        for metric, func in [("average", statistics.mean), ("median", statistics.median), ("max", max), ("min", min)]:
            for start_or_end in ["start", "end"]:
                try:
                    stats[f"{metric}_{start_or_end}_difference"] = func(stats[f"all_{start_or_end}_differences"])
                except Exception as e:
                    print(f"ERROR calculating {metric}_{start_or_end}_difference:", e)
                    stats[f"{metric}_{start_or_end}_difference"] = ""
        #stats["average_start_difference"] = sum(stats["all_start_differences"]) / len(stats["all_start_differences"])
        #stats["average_end_difference"] = sum(stats["all_end_differences"]) / len(stats["all_end_differences"])
        #stats["median_start_difference"] = statistics.median(stats["all_start_differences"])
        #stats["median_end_difference"] = statistics.median(stats["all_end_differences"])
        #stats["max_start_difference"] = max(stats["all_start_differences"])
        #stats["max_end_difference"] = max(stats["all_end_differences"])
        #stats["min_start_difference"] = min(stats["all_start_differences"])
        #stats["min_end_difference"] = min(stats["all_end_differences"])
        try: 
            stats["average_start_or_end_difference"] = str((abs(stats["average_start_difference"]) + abs(stats["average_end_difference"]))/2)
        except:
            stats["average_start_or_end_difference"] = ""

        try:
            stats["not_in_new_plus_not_in_old"] = str(int(stats["not_in_new"]) + int(stats["not_in_old"]))
        except:
            stats["not_in_new_plus_not_in_old"] = ""

        try:
            stats["start_or_end_did_not_change"] = str(int(stats["start_did_not_change"]) + int(stats["end_did_not_change"]))
        except:
            stats["start_or_end_did_not_change"] = ""

        # remove the lists of start and end differences from the stats dictionary:
        del stats["all_start_differences"]
        del stats["all_end_differences"]


def main(test_csv_folder, old_csv_folder, stats_folder, id_ms_d):
    """
    Compare the outputs from the test runs with the old passim output and store statistics.
    """
    all_stats = dict()

    if not os.path.exists(stats_folder):
        os.makedirs(stats_folder)
    detailed_stats_folder = os.path.join(stats_folder, "detailed")
    if id_ms_d:
        detailed_stats_folder += "_evaluated_milestones"
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
            "combined_in_new": 0,
            "evaluated_alignments_in_old": 0,
            "evaluated_alignments_in_new": 0
            }
        detailed_stats = dict()

        for old_output_fn in os.listdir(old_csv_folder):
            old_output_fp = os.path.join(old_csv_folder, old_output_fn)
            b1, b2 = old_output_fn.split(".csv")[0].split("_")
            test_csv_fn = find_csv(run_folder, b1, b2, rev=False)
            if test_csv_fn:
                test_csv_fp = os.path.join(run_folder, b1, test_csv_fn)
                find_srt_changes(old_output_fp, test_csv_fp, b1, b2, stats, detailed_stats, id_ms_d)
            else:
                print(run, ": no output found for", old_output_fn)
                files_not_found.append(run + " : " + old_output_fn)
        if not id_ms_d:
            del stats["evaluated_alignments_in_old"]
            del stats["evaluated_alignments_in_new"]
        all_stats[run] = stats
        outfp = os.path.join(detailed_stats_folder, run+".json")
        with open(outfp, mode="w", encoding="utf-8") as file:
            json.dump(detailed_stats, file, ensure_ascii=False,
                      indent=4, sort_keys=True)


    print("files not found:")
    for i, f in enumerate(files_not_found):
        print(i, f)

    if id_ms_d:
        outfn = "all_stats_for_evaluated_milestones"
    else:
        outfn = "all_stats"
    with open(os.path.join(stats_folder, outfn+".json"), mode="w", encoding="utf-8") as file:
        json.dump(all_stats, file, ensure_ascii=False, indent=2, sort_keys=True)

    calculate_averages(all_stats)
    tsv = json2tsv(all_stats)
    with open(os.path.join(stats_folder, outfn+".tsv"), mode="w", encoding="utf-8") as file:
        file.write(tsv)


root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(root)

files_not_found = []

test_csv_folder = os.path.join(root, "output", "csv")
old_csv_folder = os.path.join(root, "2021_1_4_outputs")
stats_folder = os.path.join(root, "stats")
id_ms_list_fp = os.path.join(root, "tagged_texts", "id_ms_list.csv")
with open(id_ms_list_fp, mode="r", encoding="utf-8") as file:
    id_ms_d = dict()
    for row in file.read().splitlines()[1:]:
        id_, start, end = [x.strip() for x in row.split(",")]
        if id_ not in id_ms_d:
            id_ms_d[id_] = []
        id_ms_d[id_].append( (int(start), int(end)) )
main(test_csv_folder, old_csv_folder, stats_folder, id_ms_d)
for i, f in enumerate(files_not_found):
    print(i, f)

