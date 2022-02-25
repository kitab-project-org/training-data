echo Removing old bash scripts
rm -rf ./bash_scripts/
echo Create new bash scripts
mkdir ./bash_scripts
python3 scripts/build_bash.py
echo  
echo Available bash scripts:
echo $(ls bash_scripts/)
run-parts --list bash_scripts/
echo Provide a filename of a bash script:
read fn
echo Executing ./bash_scripts/$fn
bash ./bash_scripts/$fn
