#!/bin/bash

# Init Bash shell prompt. This is done always to address some edge cases
export PS1="\u@${CONTAINER_NAME}:\w\\$ "

if [ -z ${init_env_executed} ]
then
  echo "Initializing environment on $CONTAINER_NAME ..."
  export init_env_executed=1
else
  echo "Environment already initialized."
  return
fi

# env.sh initializes: JAVA_HOME, SPARK_HOME, HADOOP_HOME, generated from Dockerfile.
source /env.sh

# Add spark and hadoop paths for executables
export PATH=${PATH}:${HADOOP_HOME}/bin/:${HADOOP_HOME}/sbin/:${SPARK_HOME}/bin/:${SPARK_HOME}/sbin/:${JAVA_HOME}/bin

# From https://spark.apache.org/docs/latest/hadoop-provided.html
export SPARK_DIST_CLASSPATH=$(hadoop classpath)

# Use hadoop native libraries
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${HADOOP_HOME}/lib/native/

# Keep spark master and slaves in foreground
export SPARK_NO_DAEMONIZE=1

# Required for YARN mode
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop/

# Set Python path, without a fixed predefined py4j version
export PYTHONPATH=${PYTHONPATH}:/shared:${SPARK_HOME}/python:$(realpath ${SPARK_HOME}/python/lib/py4j-*-src.zip)

