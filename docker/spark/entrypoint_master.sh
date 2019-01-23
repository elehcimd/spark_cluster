#!/bin/bash

# Initialise environment profile and container name
echo "export PROFILE=$PROFILE CONTAINER_NAME=$CONTAINER_NAME" >>/root/.bashrc

# Initialize env variables
source /shared/docker/spark/init_env.sh

### Start HDFS

# start SSH service
service ssh start

# To be executed at runtime (this requires sshd already running)
ssh-keyscan spark-master,localhost,0.0.0.0 > /root/.ssh/known_hosts

# format HDFS name node folder only if not existing (otherwise, reuse it!)
test ! -d /data/hdfs/nn && hdfs namenode -format
start-dfs.sh

### Start YARN

start-yarn.sh

# Start Spark master node
start-master.sh

