# **isnad classifier training data**

## **Folder structure**

### 'Human tags' : 

Contains all files entirely tagged or reviewed by a human. It should not contain files tags that have not been reviewed.

**NOTE:**
*For all files that are manually tagged, ensure that you update the csv file logging which lines have been manually tagged*

### 'Auto tags for review' : 

Contains files tagged by the model awaiting review.

**NOTE:** 
*Un-reviewed files use the extension '.auto_tagged'*
*Reviewed files use the extension '.reviewed'*

*For all reviewed files, ensure to update the csv file logging which lines have been reviewed*

## **Tags**

For all files, the following tags are used:

| In-text Tag | Meaning |
| --- | --- |
| @Isnad_Beg@ | Indicates where an isnad begins |
| @Isnad_End@ | Indicates where an isnad ends |

