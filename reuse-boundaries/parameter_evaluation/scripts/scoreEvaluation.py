# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:46:47 2023

@author: mathe
"""

import pandas as pd

def scoreEvaluation(scoringCsv, evaluatedMs, outPath):
    
    # Load in the scoring csv drop columns that are not for evaluation
    scoringDf = pd.read_csv(scoringCsv)
    scoringDf = scoringDf.loc[:, (scoringDf == "t").any()]
    
    evaluatedDict = pd.read_table(evaluatedMs).to_dict("records")
    
    for row in evaluatedDict:
        score = 0
        for idx, columnName in enumerate(scoringDf.columns):
            value = row[columnName]
            lowerBound = int(scoringDf.iloc[4, idx])
            upperBound = int(scoringDf.iloc[5, idx])
            fixedScore = int(scoringDf.iloc[6, idx])
            if lowerBound >= value: 
                gap = lowerBound - value
                score = score + gap*fixedScore
            elif value >= upperBound:
                gap = value - upperBound
                score = score + gap*fixedScore
    
                
        row["score"] = score
    
    evaluatedDf = pd.DataFrame(evaluatedDict)
    evaluatedDf = evaluatedDf.sort_values(by=['score'])
    print(evaluatedDf.head().transpose())
    evaluatedDf.to_csv(outPath, index=False)


scoringCsv = "C:/Users/mathe/Documents/Github-repos/training-data/reuse-boundaries/parameter_evaluation/stats/all_stats_for_evaluated_milestones_min_max_median_scoring.tsv"
evaluatedMs = "C:/Users/mathe/Documents/Github-repos/training-data/reuse-boundaries/parameter_evaluation/stats/all_stats_for_evaluated_milestones.tsv"
outPath = "C:/Users/mathe/Documents/Github-repos/training-data/reuse-boundaries/parameter_evaluation/stats/all_stats_for_evaluated_milestones_scored.csv"
                
scoreEvaluation(scoringCsv, evaluatedMs, outPath)  
    
    
    