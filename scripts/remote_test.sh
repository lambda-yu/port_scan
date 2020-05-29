#!/usr/bin/bash
# 运行方式
# remote_test.sh masscan执行文件位置 回传ip:port

path=$1
back_url=$2
log_time="`date +%Y-%m-%d`"
log_path="/home/scan/logs/daemon_log"" ${log_time}.log"


#　masscan安装检测
if [ ! -e $path ]; then
	masscan="masscan not exists"
else
	masscan="masscan is exists"
	# 获取最大速度
	if [ ! -e "/home/scan/test.csv" ] && [ -e "/home/scan/speed_test" ]; then
		speed=`cat /home/scan/speed_test | tr '\r\n' '\n'| cat | grep remaining | sort -rn -t " " -k 2 | head -1 | awk -F ',' '{print $1}'| awk -F ':' '{print $2}'`
		rm -rf "/home/scan/speed_test"
	else
		speed=""
	fi
fi

# 磁盘容量检查
disk_total=`df | grep -w / |awk '{print int($2)}'`
disk_used=`df | grep -w / |awk '{print int($3)}'`
disk_free=$((${disk_total%?}-${disk_used%?}))

# 检测核心数量
cpu_num=`cat /proc/cpuinfo |grep "physical id"|sort|uniq|wc -l`
cpu_core_num=`cat /proc/cpuinfo |grep "cpu cores"|uniq|wc -l`
cpu_core_thread_num=`cat /proc/cpuinfo |grep "processor"|wc -l`
cpu=$((cpu_num*cpu_core_num*cpu_core_thread_num))

# 检测空闲内存大小
# memtotal=`cat /proc/meminfo | grep MemTotal|awk '{print $2}'`
memfree=`cat /proc/meminfo | grep MemFree|awk '{print $2}'`


while true;
do
	# 回传给主服务器
	curl -d "{\"cpu\": \"${cpu}\", \"memory_free\": \"${memfree}KB\", \"disk_free\": \"${disk_free}KB\", \"masscan\": \"${masscan}\", \"max_speed\": \"${speed/,/}\"}" -H "Content-Type: application/json" $back_url > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    break
	else
		time=`date +%Y-%m-%d-%H:%M:%S`
		echo "[$time]: the $back_url server error" >> "$log_path"
		sleep 5
  fi
done
exit 0
