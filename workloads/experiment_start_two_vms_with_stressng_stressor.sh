#!/bin/bash

iterations=40
ns=(3125 6250 9375 12500 50000)
periods=(0.032 0.016 0.012 0.008 0.002)
stress=(0 20 40 60 80 100)

for ((iter=0;iter<$iterations;iter++))
do
	for idx in "${!ns[@]}"
	do
		n=${ns[$idx]}
		p=${periods[$idx]}

		for s in "${stress[@]}"
		do

			START=$(date +%s)
			echo "Num: $n Period: $p Stress CPU: $s Start time: " >> ./logs/experiment_timestamps_$iter.txt
			echo $START >> ./logs/experiment_timestamps_$iter.txt


			if [ $s != 0 ]
			then
				# Database
				ssh -A ubuntu@<insert-ip-address> CPUPER=$s "bash -s" < ./start_stress.sh
				# Web Server
				ssh -A ubuntu@<insert-ip-address> CPUPER=$s "bash -s" < ./start_stress.sh
			fi

			echo "STARTING HTTPERF"

			taskset 0x00000001 httperf --server <insert-ip-address> --port 9080 --http-version=1.1 --wsesslog=$n,1,acme_session.txt --add-header='Content-Type:application/json\n' --session-cookie --period=e$p > ./logs/httperf_acme_output_${n}_${p}_${s}_$iter.txt


			echo "Num: $n Period: $p Stress CPU: $s End time: " >> ./logs/experiment_timestamps_$iter.txt
			END=$(date +%s)
			echo $END >> ./logs/experiment_timestamps_$iter.txt

			# Database
			ssh -A ubuntu@<insert-ip-address> < ./teardown.sh
			# Web Server
			ssh -A ubuntu@<insert-ip-address> < ./teardown.sh

			sleep 2

		done
	done
done