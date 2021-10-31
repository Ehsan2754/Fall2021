FROM hadoop-base:latest

WORKDIR /hadoop

# we set an environment variable pointing to the folder with configuration files for convenience
ENV HADOOP_CONF_DIR=/hadoop/etc/hadoop

# Setup passphraseless ssh
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
RUN cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
RUN chmod 0600 ~/.ssh/authorized_keys

# every new container will come with pre-formatted HDFS
RUN hdfs namenode -format

# copy configuration files
COPY hadoop-conf $HADOOP_CONF_DIR

# copy the run script and make it executable
COPY run.sh /hadoop
RUN chmod +x run.sh

# we will need to bind these ports when instantiating a new container to make web-interfaces available
# read https://docs.docker.com/engine/reference/builder/#expose for more info
# namenode
EXPOSE 9870 
# resource manager 
EXPOSE 8088 
# node manager
EXPOSE 8042 

# set default run script
CMD /hadoop/run.sh