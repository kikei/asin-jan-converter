FROM ubuntu:latest

# Setup Ubuntu
RUN apt-get update
RUN apt-get install -y tor cron

# Setup cron
COPY config-cron /root
RUN crontab /root/config-cron

# Setup tor
COPY torrc /etc/tor/torrc

# Start cron and tor
CMD /etc/init.d/cron start && tor
