# **isnad classifier training data**

## **Folder structure**

### 'Human tags' : 

Contains all files entirely tagged or reviewed by a human. It should not contain files tags that have not been reviewed.

**NOTE:**
*For all files that are manually tagged, ensure that you update isnadtaggedlocations.json logging which lines have been manually tagged*

### 'Auto tags for review' : 

Contains files tagged by the model awaiting review.


### 'Reviewed tags' :

Contains files with automatic tags that have been reviewed

*For all reviewed files, ensure to update isnadtaggedlocations.json logging which lines have been reviewed*

## **Tags**

For all files, the following tags are used (subject to change following review):

| In-text Tag | Meaning |
| --- | --- |
| @Isnad_Beg@ | Indicates where an isnad begins |
| @Isnad_End@ | Indicates where an isnad ends |


## **Process summary for training data creation or review**

**NOTE:** *Gitbash commands detailed below are similar to those followed for OpenITI mARkdown, described in step [here:](https://docs.google.com/document/d/1XsRR56gn3LvpToTtmy7_YlLtG9bybZImhVMvX1SISrE/edit?usp=sharing "OpenITI mARkdown Annotation workflow")* 

  1. update your local repository in git bash using command 'git pull origin master' (ensure that you are in the 'training-data' repository in Gitbash before pulling.)

  1. Choose a file to tag from Priority list.csv

  1. Annotate the file from a random starting place, taking a careful note of the line number 
  **IMPORTANT: IT IS ESSENTIAL TO NOTE THE EXACT LINES THAT HAVE BEEN HUMAN-READ FOR THE MODEL TO WORK EFFECTIVELY**

  1. Tag the isnads in the file file for 2000 lines, using the markers given above. You may annotate in smaller sections across the text (e.g. from lines 2400-2900, lines 4000-4500, lines, lines 6200-6700, and lines 8100-8600).

  1. **if you are reviewing an auto-tagged file:** correct all of the isnad tags in the 2000 lines you are reviewing, deleting or moving erronous tags.

  1. Once 2000 lines are tagged, save the file. Open isnadtaggedlocations.json

  1. **if your text is on the list in the json file and has been tagged before:** add the lines that you have reviewed after 'taggedSections' using a comma to separate it from the previous tagged lines and in square brackets with a comma separating the first line tagged and the line following that tagged e.g.: [[1000,1200],[1500,1600]], and add your name to the annotators value, separating from the previous annotator with a comma, e.g.: "Previous Person, Second Person"
 
  1. **if your text is new**: Add a new line to the json file, copy the template the new line, fill out the template with your details.
  **NOTE:** When noting lines tagged, the first number includes the text you have reviewed and the second number the line after you have finished review. E.g. if you read and tagged lines 1100-1200, you would write [1100,1201].

  1. Save the json file.

### **Pushing back to GitHub**
  1. Go to gitbash, in gitbash go to the training-data folder
  1. Type: git add .
  1. Press enter
  1. Type: git commit -m"ENTER YOUR COMMENT HERE"
  1. Press enter
  1. Type: git push origin master
  1. Press enter
  1. Your local changes are now updated on the training data repository

