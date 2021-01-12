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

For all files, the following tags are used: 

| *New tag* | Meaning | Old Tag *do not use* |
| --- | --- | --- |
| @ISB@ | Indicates where an isnad begins | @Isnad_Beg@ |
| @ISE@ | Indicates where an isnad ends | @Isnad_End@ |

*NOTE: the tags have now changed to mARkdown compatible tags. Tags must be in all caps and between @ for the mARkdown to work. If correctly entered the tags will be highlighted*

## **Process summary for training data creation or review**

### **Useful links:** 

*Gitbash commands detailed below are similar to those followed for OpenITI mARkdown, described [here](https://docs.google.com/document/d/1XsRR56gn3LvpToTtmy7_YlLtG9bybZImhVMvX1SISrE/edit?usp=sharing "OpenITI mARkdown Annotation workflow")* 

*For tagging guidelines, see [here](https://docs.google.com/document/d/19IPG3APp8IIq8kENLSGEFCcCSEqrgEeOxjg6dm4WKH8/edit?usp=sharing "Guidelines for Tagging Isnads"). This is a working document and will be updated as part of the weekly meetings* 

### **Process:**

  1. update your local repository in git bash using command 'git pull origin master' (ensure that you are in the 'training-data' repository in Gitbash before pulling.)

  1. Choose a file to tag from Priority list.csv. **IMPORTANT: If choosing a new file to tag from OpenITI, always use the file in mARkdown**

  1. Annotate the file from a random starting place, taking a careful note of the line number
  **IMPORTANT: IT IS ESSENTIAL TO NOTE THE EXACT LINES THAT HAVE BEEN HUMAN-READ FOR THE MODEL TO WORK EFFECTIVELY**

  1. Tag the isnads in the file file for 2000 lines, using the markers given above. You may annotate in smaller sections across the text (e.g. from lines 2400-2900, lines 4000-4500, lines, lines 6200-6700, and lines 8100-8600).

  1. **if you are reviewing an auto-tagged file:** correct all of the isnad tags in the 2000 lines you are reviewing, deleting or moving erronous tags.

  1. Once 2000 lines are tagged, save the file. Open isnadtaggedlocations.json

  1. **if your text is on the list in the json file and has been tagged before:** add the lines that you have reviewed after 'taggedSections' using a comma to separate it from the previous tagged lines and in square brackets with a comma separating the first line tagged and the line following that tagged e.g.: [[1000,1200],[1500,1600]], and add your name to the annotators value, separating from the previous annotator with a comma, e.g.: "Previous Person, Second Person"
 
  1. **if your text is new**: Add a new line to the json file, copy the template the new line, fill out the template with your details.
  **NOTE:** When noting lines tagged, the first number includes the text you have reviewed and the second number the line after you have finished review. E.g. if you read and tagged lines 1100-1200, you would write [1100,1201].

  1. Save the json file.

  1. **if you are reviewing an auto-tagged file:** Move the tagged file from the 'Autotags for review' folder to the 'Reviewed tags' folder.

### **Pushing back to GitHub**
  1. Go to gitbash, in gitbash go to the training-data folder
  1. Type: git add .
  1. Press enter
  1. Type: git commit -m"ENTER YOUR COMMENT HERE"
  1. Press enter
  1. Type: git pull origin master *(always pull before you push to avoid merge conflicts)*
  1. Press enter
  1. Type: git push origin master
  1. Press enter
  1. Your local changes are now updated on the training data repository

## **Isnad comments file**

Add to this file any isnads for which queries arise when tagging. 

**For each isnad provide:** the text URI, starting line of queried isnad, excerpt of Arabic text with the proposed isnad tags inserted and a short comment

**Feedback:** During each discussion session, feedback will be provided on the queried excerpts. If the tagging was corrected, the corrected excerpt will be found in the 'Corrected excerpt' column of the csv.

## **Acknowledgements**

The data in this repository was created using [OpenITI texts](https://github.com/openiti "to see openITI repositories"), and the isnads automatically tagged using a model that is intended for tagging isnads in a broad range of texts (that is, not just hadith). The model is being developed by computer science student Ryan Muther.

### **Annotators/evaluators**
Ryan Muther's isnad model relies on supervised training data (and the main purpose of this repository is for the version control of this training data). The annotators involved in tagging isnads for this project are as follows:

Mathew Barber
Hamid Reza Hakimi
Ahmed Hassan
Kevin Jacques
Simon Loynes
Lorenz Nigst
Sarah Savant

isnadTaggedLocations.json identifies the specific involvement of each team member. Not only did these annotators tag isnads within a broad range of texts but they discussed the process of identifying and tagging isnads in a weekly meeting. This meeting and the annotation was invaluable for developing the model to tag isnads.

