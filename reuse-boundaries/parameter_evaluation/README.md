# Testing parameters for passim

The team has done manual evaluations of passim outputs.

We are now going to run passim on the sections the team checked
using different combinations of parameters:

| Parameter   | default value | min value | max value | increment | base       | different values |
| --min-match | 5             | 3         | 10        | 1         | ngrams     | 8                |
| --min-align | 20            | 7         | 25        | 1         | tokens     | 19               |
| n-grams     | 5             | 3         | 7         | 1         | tokens     | 5                |
| gap         | 100           | 25        | 200       | 25        | characters | 8                |

# Usage

Run the bash script "run.sh": `bash ./run.sh`

This script will: 

* remove the existing bash scripts in the bash_scripts folder
* create new bash scripts:
  - one bash script file per text pair
  - each bash script file will run passim for any parameter combinations that have not been tried yet
  - create csv output based on passim output
  - remove the raw passim output
  - push csv output to GitHub
* ask user input for which text pair bash script to run, and run that bash script.
