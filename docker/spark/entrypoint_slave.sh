#!/bin/bash

# Initialise environment profile and container name
echo "export PROFILE=$PROFILE CONTAINER_NAME=$CONTAINER_NAME" >>/root/.bashrc

# Initialize env variables
source /shared/docker/spark/init_env.sh

# Start Spark slave node
start-slave.sh spark://spark-master:7077
