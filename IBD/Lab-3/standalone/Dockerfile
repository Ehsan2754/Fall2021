FROM hadoop-base:latest

WORKDIR /hadoop

COPY run.sh /hadoop
# make this script executable. otherwise, you will see errors
RUN chmod +x run.sh

# the default command executed when you do docker run
CMD bash run.sh