# use standard Ubuntu image as the base
FROM ubuntu

# set environment variable with your Hadoop version
ENV HADOOP_VERSION 3.3.0
# Hadoop installation will reside in /hadoop
WORKDIR /hadoop
COPY hadoop-$HADOOP_VERSION /hadoop

# ubuntu image is a bare minimum. install necessary packages
RUN apt-get update && apt-get install openjdk-8-jre ssh -y

# set environment variables that might be useful in the future
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV HADOOP_HOME /hadoop
ENV PATH /hadoop/sbin:/hadoop/bin:$PATH

# Hadoop frowns upon running its services as the root user. Let's convince it is necessary by setting environment variables
ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

# we do not have CMD or ENTRYPOINT set in this image
