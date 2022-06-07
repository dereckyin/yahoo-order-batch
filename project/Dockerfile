FROM python:3.9.0-slim-buster

ENV TZ="Asia/Taipei"
RUN date

# set working directory
WORKDIR /usr/src/app

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# install oracle client
RUN apt-get update && apt-get install -y libaio1 wget unzip iputils-ping curl cron coreutils

ADD samplecron /etc/cron.d/samplecron
RUN chmod 0644 /etc/cron.d/samplecron 
RUN crontab /etc/cron.d/samplecron
RUN touch /var/log/cron.log
# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip && \
    unzip instantclient-basiclite-linuxx64.zip && rm -f instantclient-basiclite-linuxx64.zip && \
    cd /opt/oracle/instantclient* && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig
RUN python -m pip install cx_Oracle

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

RUN cron