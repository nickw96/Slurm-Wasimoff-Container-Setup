@echo OFF
py evaluation/generate_table.py -d data-ex1 -s 50 -n 3
py evaluation/generate_table.py -d data-ex1-control -s 50 -n 3
py evaluation/generate_table.py -d data-ex2 -s 1 -n 3
py evaluation/generate_table.py -d data-ex3 -s 50 -n 3
py evaluation/generate_table_ex2.py -d data-ex2