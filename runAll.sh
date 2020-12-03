#!/bin/bash

python3 ./buildGraph.py ./configs/basic_problem_1.json
python3 ./main.py ./configs/basic_problem_1.json ./configs/sol_to_basic_problem_1.json

python3 ./buildGraph.py ./configs/basic_problem_2.json
python3 ./main.py ./configs/basic_problem_2.json ./configs/sol_to_basic_problem_2.json

python3 ./buildGraph.py ./configs/goal_keeper_problem_1.json
python3 ./main.py ./configs/goal_keeper_problem_1.json ./configs/sol_to_goal_keeper_problem_1.json

python3 ./buildGraph.py ./configs/initial_defenders_problem_1.json
python3 ./main.py ./configs/initial_defenders_problem_1.json ./configs/sol_to_initial_defenders_problem_1.json

python3 ./buildGraph.py ./configs/min_dist_problem_1.json
python3 ./main.py ./configs/min_dist_problem_1.json ./configs/sol_to_min_dist_problem_1.json

python3 ./buildGraph.py ./configs/multigoal_problem_1.json
python3 ./main.py ./configs/multigoal_problem_1.json ./configs/sol_to_multigoal_problem_1.json