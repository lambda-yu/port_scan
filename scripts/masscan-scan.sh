#!/usr/bin/bash
# 运行方式
# remote_test.sh 1.masscan位置 2.conf位置 3.PID回传地址 4.任务执行完成回传地址

log_time="`date +%Y-%m-%d`"
log_path="/home/scan/logs/daemon_log"" ${log_time}.log"

function run() {
	masscan_path=$1
	conf_path=$2
	job_id=$3
	pid_back=$4
	call_back=$5

	declare -A conf_dict

	while true;
	do
		# 判断配置文件是否存在
		if [ ! -f "$conf_path" ]; then
			time=`date +%Y-%m-%d-%H:%M:%S`
			echo "[$time]: the job $job_id config file is not exists" >> "$log_path"
			sleep 5
			continue
		fi

		# 获取配置文件
		for conf in `cat $conf_path`;
		do
			conf_dict[`echo $conf | awk -F '=' '{print $1}'`]=`echo $conf | awk -F '=' '{print $2}'`
		done

		# 如果运行使能为false则不进行扫描
		if [ "${conf_dict['run_enable']}" != "true" ];
		then
			time=`date +%Y-%m-%d-%H:%M:%S`
			echo "[$time]: the job $job_id is pause" >> "$log_path"
			sleep 5
			continue
		fi

		# 执行扫描
		time=`date +%Y-%m-%d-%H:%M:%S`
		data_path=${conf_dict['save_path']}"/$job_id""<$time>.csv"
		`sudo $masscan_path --range ${conf_dict['host']} -p ${conf_dict['port']} --rate=${conf_dict['rate']} -oL "$data_path" > /home/scan/logs/${job_id}"_status" 2>&1` &

		masscan_pid=$!

		while true;
		do
			# masscan_pid回传
			curl -d "{\"job_id\": \"${job_id}\", \"masscan_pid\": \"${masscan_pid}\"}" -H "Content-Type: application/json" $pid_back > /dev/null 2>&1
			if [ $? -eq 0 ]; then
				break
			else
				time=`date +%Y-%m-%d-%H:%M:%S`
				echo "[$time]: the $pid_back server error" >> "$log_path"
				sleep 5
			fi
		done

		wait $masscan_pid
		masscan=$?

		if [ $masscan == "0" ]; then
			status="success"
		else
			status="failed"
		fi
		while true;
		do
			# 任务结果回传给主服务器
			curl -d "{\"job_id\": \"${job_id}\", \"status\": \"${status}\", \"data_path\": \"$data_path\"}" -H "Content-Type: application/json" $call_back > /dev/null 2>&1
			if [ $? -eq 0 ]; then
				break
			else
				time=`date +%Y-%m-%d-%H:%M:%S`
				echo "[$time]: the $call_back server error" >> "$log_path"
				sleep 5
			fi
		done
		rm -rf /home/scan/logs/${job_id}"_status"
	done
}

masscan_path=$1
conf_path=$2
pid_call_back=$3
result_call_back=$4


# 从配置文件名中获得job_id
job_id=$(echo ${conf_path} | awk -F '.' '{print $1}')
job_id=${job_id##*/}

run $masscan_path $conf_path $job_id $pid_call_back $result_call_back &
pid=$!

while true;
do
	# 任务PID回传给主服务器
	curl -d "{\"job_id\": \"${job_id}\", \"job_pid\": \"${pid}\"}" -H "Content-Type: application/json" $pid_call_back > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    break
	else
		time=`date +%Y-%m-%d-%H:%M:%S`
		echo "[$time]: the $pid_call_back server error" >> "$log_path"
		sleep 5
  fi
done
exit 0