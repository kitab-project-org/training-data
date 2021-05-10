# **Boundary of reuse evaluations**

This repo contains the evaluation for text reuse boundaries produced by passim analysis. **For-evaluation** contains passim outputs using the 'Automatic' tags outlined in the table below, and are files that have not recieved any human evaluation. **Evaluated** contains files where the 'Automatic' tags have been checked and replaced with 'Manual' tags. 

The purpose of this study is not to judge the internal quality of each passim alignment, but to check if the edges of each alignment are correct. I.e. is there more text reuse above or before the automatic alignment boundaries, or does the alignment start too early or finish too late?

When evaluators check these files, they mark the line range they have evaluated in 'EvaluationLocations.json'. When noting lines tagged, the first number includes the text that has been reviewed and the second number the line after the reviewed text. E.g. if the evaluator read and re-tagged lines 1100-1200, they would write [1100,1201].

### Text reuse tagging schemes

*Brackets indicate optional part of scheme and 'SOR' stands for a three-letter abbreviation for the corresponding source. For example, Ibn al-Athir's Kamil might use @KAM@ALB@*

| Manual Beginning tag | Manual End tag | Automatic Beginning tag | Automatic End tag |
|---|---|---|---|
| (@SOR)@ALB@ | (@SOR)@ALE@ | (@SOR)@ALIGN@B@0@ | (@SOR)@ALIGN@E@0@ |


If the annotation scheme is correctly applied, the 'Test patterns' file found under the mARkdown-training-data folder should appear in EditPad Pro as below:

![Sample annotation](https://github.com/kitab-project-org/training-data/blob/master/mARkdown-training-data/Sample%20annotation.png)