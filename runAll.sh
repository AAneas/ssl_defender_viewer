#!/bin/bash

S1=$(date +%s%N)
python3 ./buildGraph.py ./configs/basic_problem_1.json
E1=$(date +%s%N)
D1=$((($E1 - $S1)/1000000))
echo "(basic_problem_1 took $D1 miliseconds)" >| solTime.txt

S2=$(date +%s%N)
python3 ./buildGraph.py ./configs/basic_problem_2.json
E2=$(date +%s%N)
D2=$((($E2 - $S2)/1000000))
echo "(basic_problem_2 took $D2 miliseconds)" >> solTime.txt

S3=$(date +%s%N)
python3 ./buildGraph.py ./configs/goal_keeper_problem_1.json
E3=$(date +%s%N)
D3=$((($E3 - $S3)/1000000))
echo "(goal_keeper_problem_1 took $D3 miliseconds)" >> solTime.txt

S4=$(date +%s%N)
python3 ./buildGraph.py ./configs/initial_defenders_problem_1.json
E4=$(date +%s%N)
D4=$((($E4 - $S4)/1000000))
echo "(initial_defender_problem_1 took $D4 miliseconds)" >> solTime.txt

S5=$(date +%s%N)
python3 ./buildGraph.py ./configs/min_dist_problem_1.json
E5=$(date +%s%N)
D5=$((($E5 - $S5)/1000000))
echo "(min_dist_problem_1 took $D5 miliseconds)" >> solTime.txt

S6=$(date +%s%N)
python3 ./buildGraph.py ./configs/multigoal_problem_1.json
E6=$(date +%s%N)
D6=$((($E6 - $S6)/1000000))
echo "(multigoal_problem_1 took $D6 miliseconds)" >> solTime.txt

S7=$(date +%s%N)
python3 ./buildGraph.py ./configs/max_speed_problem_1.json
E7=$(date +%s%N)
D7=$((($E7 - $S7)/1000000))
echo "(max_speed_problem_1 took $D7 miliseconds)" >> solTime.txt

python3 ./main.py ./configs/basic_problem_1.json ./configs/sol_to_basic_problem_1.json
python3 ./main.py ./configs/basic_problem_2.json ./configs/sol_to_basic_problem_2.json
python3 ./main.py ./configs/goal_keeper_problem_1.json ./configs/sol_to_goal_keeper_problem_1.json
python3 ./main.py ./configs/initial_defenders_problem_1.json ./configs/sol_to_initial_defenders_problem_1.json
python3 ./main.py ./configs/min_dist_problem_1.json ./configs/sol_to_min_dist_problem_1.json
python3 ./main.py ./configs/multigoal_problem_1.json ./configs/sol_to_multigoal_problem_1.json
python3 ./main.py ./configs/max_speed_problem_1.json ./configs/sol_to_max_speed_problem_1.json