python3 extractBEN.py --generate 400000000 --produce 500 --nodealer True >pbs.sh
./pbs.sh
python3 removedate.py
python3 rotate.py