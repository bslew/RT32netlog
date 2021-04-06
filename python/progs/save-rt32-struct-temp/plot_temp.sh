#!/bin/bash

f=$1
#rt32-struct-temp-monitor-line-lab-cooling-heating-test.csv
cat $f | awk 'NR>1 {print $0}' > test.dat
plot_function.py test.dat -t ts -x 12 --big --rows -1 \
		 --dateFmt "%Y-%m-%d %H:%M:%S" \
		 -y 5 -l T21_1 \
		 -y 1 -l T21_2 \
		 -y 4 -l T21_3 \
		 -y 11 -l T25_1 \
		 -y 8 -l T25_2 \
		 -y 2 -l T25_3 \
		 -y 0 -l T30_1 \
		 -y 3 -l T40_1 \
		 -y 9 -l T40_2 \
		 -y 6 -l T50_1 \
		 -y 7 -l T50_2 \
		 -y 10 -l T50_3
		            
