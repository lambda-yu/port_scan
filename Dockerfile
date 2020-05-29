FROM python:3.7.5

ENV TZ=Asia/Shanghai
RUN mkdir -p /port_scan_code
RUN mkdir -p /logs
ADD . /port_scan_code
WORKDIR /port_scan_code

RUN pip3 install -r requirements.txt
RUN chmod +x start_service.sh

CMD ["./start_service.sh"]
