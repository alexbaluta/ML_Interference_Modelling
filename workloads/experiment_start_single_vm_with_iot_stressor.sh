#!/bin/bash

iterations=40
ns=(3125 6250 9375 12500 50000)
periods=(0.032 0.016 0.012 0.008 0.002)
wkld_intensities=(0 1 2 3 4 5)

for ((iter=0;iter<$iterations;iter++))
do
	for idx in "${!ns[@]}"
	do
		n=${ns[$idx]}
		p=${periods[$idx]}

		for s in "${!wkld_intensities[@]}"
		do

			START=$(date +%s)
			wkld_intensity=${wkld_intensities[$s]}
			
			echo "Num: $n Period: $p Stress N: $wkld_intensity Start time: " >> ./logs/experiment_timestamps_$iter.txt
			echo $START >> ./logs/experiment_timestamps_$iter.txt

			if [ $s != 0 ]
			then
				/home/ubuntu/jmeter/apache-jmeter-5.4.1/bin/jmeter.sh -n -t /home/ubuntu/jmeter/apache-jmeter-5.4.1/bin/Jmeter.13/WorkloadRevised/TestPlan1.0$s.jmx -J TestIP=<insert-ip-address> &
			fi

			echo "STARTING HTTPERF"

			taskset 0x00000001 httperf --server <insert-ip-address> --port 9080 --http-version=1.1 --wsesslog=$n,1,acme_session.txt --add-header='Content-Type:application/json\n' --session-cookie --period=e$p > ./logs/httperf_acme_output_${n}_${p}_${wkld_intensity}_$iter.txt

			echo "Num: $n Period: $p Stress N: $wkld_intensity End time: " >> ./logs/experiment_timestamps_$iter.txt
			END=$(date +%s)
			echo $END >> ./logs/experiment_timestamps_$iter.txt

			if [ $s != 0 ]
			then
				sudo pkill -f "/home/ubuntu/jmeter/apache-jmeter-5.4.1/bin/ApacheJMeter.jar"
			fi

			sleep 2

		done
	done
done