#!/bin/bash

echo "Résultats des tests :" >| solTime.txt
echo "-Modifions pos_step :" >> solTime.txt
for ps in $(seq 1 10)
do
    #echo "$ps" >> solTime.txt
    tps=$(printf '%.2f' $(echo "scale=2; $ps/20" | bc -l))
    #echo "$tps" >> solTime.txt
    python3 ./randomProblem.py -ps $tps
    T=0
    T1=0
    T2=0
    for nb in $(seq 1 10)
    do
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    T2=$(($T2/10))
    T3=$(($T3/10))
    echo "(basic_problem_1 with ps=$tps took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
    echo "(basic_problem_1 with ps=$tps took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
    echo "(basic_problem_1 with ps=$tps took $T3 miliseconds with no option, succeeded = $result3)" >> solTime.txt
done

echo "-Modifions field_limits :" >> solTime.txt
for x in $(seq 1 20)
do
    xp=$(printf '%.1f' $(echo "scale=1; $x/2" | bc -l))
    xn=$(printf '%.1f' $(echo "scale=1; $x/-2" | bc -l))
    for y in $(seq 1 20)
    do
        #echo "$ps" >> solTime.txt
        yp=$(printf '%.1f' $(echo "scale=1; $y/2" | bc -l))
        yn=$(printf '%.1f' $(echo "scale=1; $y/-2" | bc -l))
        fl="[[$xn,$xp],[$yn,$yp]]"
        #echo "$tps" >> solTime.txt
        python3 ./randomProblem.py -fl $fl
        T=0
        T1=0
        T2=0
        for nb in $(seq 1 10)
        do
            #python3 randomProblem.py -ps
            S1=$(date +%s%N)
            result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T=+$((($E1 - $S1)/1000000+$T))

            S1=$(date +%s%N)
            result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T2=+$((($E1 - $S1)/1000000+$T2))

            S1=$(date +%s%N)
            result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T3=+$((($E1 - $S1)/1000000+$T3))
        done
        T=$(($T/10))
        echo "(basic_problem_1 with fl=$fl took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
        T2=$(($T2/10))
        echo "(basic_problem_1 with fl=$fl took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
        T2=$(($T2/10))
        echo "(basic_problem_1 with fl=$fl took $T3 miliseconds, succeeded = $result3)" >> solTime.txt
    done
done

echo "-Modifions goals avec un but :" >> solTime.txt
for g in $(seq 1 6)
do
    #echo "$ps" >> solTime.txt
    gp=$(printf '%.2f' $(echo "scale=2; $g/2" | bc -l))
    gn=$(printf '%.2f' $(echo "scale=2; $g/(-2)" | bc -l))
    tg="[[[4.5,$gn],[4.5,$gp]],[-1,0]]"
    #echo "$tps" >> solTime.txt
    python3 ./randomProblem.py -mg $tg
    T=0
    T1=0
    T2=0
    for nb in $(seq 1 10)
    do
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with g=$tg goals took $T miliseconds, succeeded = $result)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with g=$tg goals took $T2 miliseconds, succeeded = $result2)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with g=$tg goals took $T3 miliseconds, succeeded = $result3)" >> solTime.txt
done

echo "-Modifions goals avec plusieurs buts :" >> solTime.txt
for mg in $(seq 1 10)
do
    #echo "$ps" >> solTime.txt
    #tps=$(printf '%.2f' $(echo "scale=2; $ps/100" | bc -l))
    #echo "$tps" >> solTime.txt
    T=0
    results=0
    T2=0
    results2=0
    T3=0
    results3=0
    for nb in $(seq 1 10)
    do
        python3 ./randomProblem.py -mg $mg
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results=$((results+1))
        fi
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results2=$((results2+1))
        fi
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results3=$((results3+1))
        fi
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with $mg goals took $T miliseconds with -kd, succeeded $results times)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with $mg goals took $T2 miliseconds with -co, succeeded $results2 times)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with $mg goals took $T3 miliseconds, succeeded $results3 times)" >> solTime.txt
done

echo "-Modifions opponents :" >> solTime.txt
for mo in $(seq 1 8)
do
    #echo "$ps" >> solTime.txt
    #tps=$(printf '%.2f' $(echo "scale=2; $ps/100" | bc -l))
    #echo "$tps" >> solTime.txt
    T=0
    results=0
    T2=0
    results2=0
    T3=0
    results3=0
    for nb in $(seq 1 10)
    do
        python3 ./randomProblem.py -mo $mo
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results=$((results+1))
        fi
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results2=$((results2+1))
        fi
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results3=$((results3+1))
        fi
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with $mg opponents took $T miliseconds with -kd, succeeded $results times)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with $mg opponents took $T2 miliseconds with -co, succeeded $results2 times)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with $mg opponents took $T3 miliseconds, succeeded $results3 times)" >> solTime.txt
done

echo "-Modifions robot_radius :" >> solTime.txt
for rr in $(seq 1 20)
do
    #echo "$ps" >> solTime.txt
    trr=$(printf '%.3f' $(echo "scale=3; $rr/100" | bc -l))
    #echo "$tps" >> solTime.txt
    python3 ./randomProblem.py -rr $trr
    T=0
    T2=0
    T3=0
    for nb in $(seq 1 10)
    do
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with rr=$trr took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with rr=$trr took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with rr=$trr took $T3 miliseconds, succeeded = $result3)" >> solTime.txt
done

echo "-Modifions theta_step :" >> solTime.txt
for ts in $(seq 1 10)
do
    #echo "$ps" >> solTime.txt
    tts=$(printf '%.3f' $(echo "scale=3; $ts/100" | bc -l))
    #echo "$tps" >> solTime.txt
    python3 ./randomProblem.py -ts $tts
    T=0
    T2=0
    T3=0
    for nb in $(seq 1 10)
    do
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with ts=$tts took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with ts=$tts took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with ts=$tts took $T3 miliseconds, succeeded = $result3)" >> solTime.txt
done

echo "-Modifions goalkeeper_area :" >> solTime.txt
for x in $(seq 1 5)
do
    xp=$(printf '%.1f' $(echo "scale=1; 9/2" | bc -l))
    xn=$(printf '%.1f' $(echo "scale=1; (9-$x)/2" | bc -l))
    for y in $(seq 1 6)
    do
        #echo "$ps" >> solTime.txt
        yp=$(printf '%.1f' $(echo "scale=1; $y/2" | bc -l))
        yn=$(printf '%.1f' $(echo "scale=1; $y/(-2)" | bc -l))
        ga="[[$xn,$xp],[$yn,$yp]]"
        #echo "$tps" >> solTime.txt
        python3 ./randomProblem.py -ga $ga
        T=0
        T2=0
        T3=0
        for nb in $(seq 1 10)
        do
            #python3 randomProblem.py -ps
            S1=$(date +%s%N)
            result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T=+$((($E1 - $S1)/1000000+$T))

            S1=$(date +%s%N)
            result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T2=+$((($E1 - $S1)/1000000+$T2))

            S1=$(date +%s%N)
            result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T3=+$((($E1 - $S1)/1000000+$T3))
        done
        T=$(($T/10))
        echo "(basic_problem_1 with ga=$ga took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
        T2=$(($T2/10))
        echo "(basic_problem_1 with ga=$ga took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
        T3=$(($T3/10))
        echo "(basic_problem_1 with ga=$ga took $T3 miliseconds, succeeded = $result3)" >> solTime.txt
    done
done

echo "-Modifions defenders :" >> solTime.txt
for md in $(seq 1 8)
do
    #echo "$ps" >> solTime.txt
    #tps=$(printf '%.2f' $(echo "scale=2; $ps/100" | bc -l))
    #echo "$tps" >> solTime.txt
    T=0
    results=0
    T2=0
    results2=0
    T3=0
    results3=0
    for nb in $(seq 1 10)
    do
        python3 ./randomProblem.py -md $md
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results=$((results+1))
        fi
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results2=$((results2+1))
        fi
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        if [ $result = "True" ]
        then
            results3=$((results3+1))
        fi
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with $md defenders took $T miliseconds with -kd, succeeded $results times)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with $md defenders took $T2 miliseconds with -co, succeeded $results2 times)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with $md defenders took $T3 miliseconds, succeeded $results3 times)" >> solTime.txt
done

echo "-Modifions ball_max_speed et robot_max_speed :" >> solTime.txt
for bs in $(seq 3 10)
do
    #xp=$(printf '%.1f' $(echo "scale=1; 9/2" | bc -l))
    #xn=$(printf '%.1f' $(echo "scale=1; (9-$x)/2" | bc -l))
    for y in $(seq 1 5)
    do
        #echo "$ps" >> solTime.txt
        #yp=$(printf '%.1f' $(echo "scale=1; $y/2" | bc -l))
        #yn=$(printf '%.1f' $(echo "scale=1; $y/(-2)" | bc -l))
        #ga="[[$xn,$xp],[$yn,$yp]]"
        #echo "$tps" >> solTime.txt
        python3 ./randomProblem.py -bs $bs -rs $rs
        T=0
        T2=0
        T3=0
        for nb in $(seq 1 10)
        do
            #python3 randomProblem.py -ps
            S1=$(date +%s%N)
            result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T=+$((($E1 - $S1)/1000000+$T))

            S1=$(date +%s%N)
            result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T2=+$((($E1 - $S1)/1000000+$T2))

            S1=$(date +%s%N)
            result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
            E1=$(date +%s%N)
            T3=+$((($E1 - $S1)/1000000+$T3))
        done
        T=$(($T/10))
        echo "(basic_problem_1 with bs=$bs and rs=$rs took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
        T2=$(($T2/10))
        echo "(basic_problem_1 with bs=$bs and rs=$rs took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
        T3=$(($T3/10))
        echo "(basic_problem_1 with bs=$bs and rs=$rs took $T3 miliseconds, succeeded = $result3)" >> solTime.txt
    done
done

echo "-Modifions min_dist :" >> solTime.txt
for mi in $(seq 1 10)
do
    #echo "$ps" >> solTime.txt
    tmi=$(printf '%.2f' $(echo "scale=2; $mi/10" | bc -l))
    #echo "$tps" >> solTime.txt
    python3 ./randomProblem.py -mi $tmi
    T=0
    T2=0
    T3=0
    for nb in $(seq 1 10)
    do
        #python3 randomProblem.py -ps
        S1=$(date +%s%N)
        result="$(echo `python3 ./buildGraph.py ./configs/random.json -kd` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T=+$((($E1 - $S1)/1000000+$T))

        S1=$(date +%s%N)
        result2="$(echo `python3 ./buildGraph.py ./configs/random.json -co` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T2=+$((($E1 - $S1)/1000000+$T2))

        S1=$(date +%s%N)
        result3="$(echo `python3 ./buildGraph.py ./configs/random.json` | cut -d'>' -f2)"
        E1=$(date +%s%N)
        T3=+$((($E1 - $S1)/1000000+$T3))
    done
    T=$(($T/10))
    echo "(basic_problem_1 with mi=$tmi took $T miliseconds with -kd, succeeded = $result)" >> solTime.txt
    T2=$(($T2/10))
    echo "(basic_problem_1 with mi=$tmi took $T2 miliseconds with -co, succeeded = $result2)" >> solTime.txt
    T3=$(($T3/10))
    echo "(basic_problem_1 with mi=$tmi took $T miliseconds, succeeded = $result3)" >> solTime.txt
done