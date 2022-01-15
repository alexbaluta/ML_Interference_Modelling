#!/bin/bash

iterations=40
ns=(3125 6250 9375 12500 50000)
periods=(0.032 0.016 0.012 0.008 0.002)
stress_ns=(0 3125 6250 9375 12500 50000)
stress_periods=(0 0.032 0.016 0.012 0.008 0.002)

for ((iter=0;iter<$iterations;iter++))
do
	for idx in "${!ns[@]}"
	do
		n=${ns[$idx]}
		p=${periods[$idx]}

		for s in "${!stress_ns[@]}"
		do

			START=$(date +%s)
			stress_n=${stress_ns[$s]}
			stress_p=${stress_periods[$s]}
			
			echo "Num: $n Period: $p Stress N: $stress_n Start time: " >> ./logs/experiment_timestamps_$iter.txt
			echo $START >> ./logs/experiment_timestamps_$iter.txt

			if [ $s != 0 ]
			then
				taskset 0x00000002 httperf --server <insert-ip-address> --port 9081 --http-version=1.1 --wsesslog=$stress_n,1,acme_session.txt --add-header='Content-Type:application/json\n' --session-cookie --period=e$stress_p &
			fi

			echo "STARTING HTTPERF"


			taskset 0x00000001 httperf --server <insert-ip-address> --port 9080 --http-version=1.1 --wsesslog=$n,1,acme_session.txt --add-header='Content-Type:application/json\n' --session-cookie --period=e$p > ./logs/httperf_acme_output_${n}_${p}_${stress_n}_$iter.txt


			echo "Num: $n Period: $p Stress N: $stress_n End time: " >> ./logs/experiment_timestamps_$iter.txt
			END=$(date +%s)
			echo $END >> ./logs/experiment_timestamps_$iter.txt

			if [ $s != 0 ]
			then
				sudo kill $(ps aux | grep 'httperf' | grep 'port 9081' | awk '{print $2}')
			fi

			sleep 2

		done
	done
done