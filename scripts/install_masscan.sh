#!/usr/bin/bash

path="home/scan/masscan/bin/masscan"
if [ ! -e $path ]; then
	# 安装环境
	`sudo apt-get update`
	`sudo apt-get -y upgrade`
	`sudo apt-get -y install git gcc make libpcap-dev`
	`git clone https://github.com/robertdavidgraham/masscan /home/scan/masscan`
	cd /home/scan/masscan
	`make`
	cd /home/scan/masscan/bin
	# 运行一次，测试速度和确认masscan安装成功,
	`./masscan 23.0.0.0/8 -p80 --rate=1000000000000 -oL /home/scan/test.csv 2> /home/scan/speed_test`

else
	`./masscan 23.1.0.0-23.5.0.0 -p80 --rate=1000000000000 -oL /home/scan/test.csv 2> /home/scan/speed_test`
fi

#　删除用于测试的文件
rm -f /home/scan/test.csv