FROM ubuntu:18.04
MAINTAINER Michele Dallachiesa <michele.dallachiesa@gmail.com>

# The root user is used as main user inside the container
USER root

# Update package list, upgrade system and set default locale
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install apt-utils
RUN apt-get -y install locales
RUN locale-gen "en_US.UTF-8"
RUN dpkg-reconfigure --frontend=noninteractive locales
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

# Install python3, and activate python3.6 as default python interpreter
RUN apt-get -y install python3-dev python3 python3-pip python3-venv
RUN pip3 install --upgrade pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1

# Install common packages
RUN apt-get -fy install wget vim net-tools inetutils-ping p7zip openssh-server ssh rsync htop

# Required for PyObject
RUN apt-get -fy install libgirepository1.0-dev libcairo2-dev

# Define Java, Hadoop and Spark versions to install
ENV JDK_VERSION 8
ENV HADOOP_VERSION 2.8.5
ENV SPARK_VERSION 2.4.5

# Install JDK
RUN apt-get -fy install openjdk-${JDK_VERSION}-jdk-headless
RUN mkdir -p /opt/hadoop

# Install hadoop separately to have native hadoop libraries
WORKDIR /tmp
RUN wget http://apache.lauf-forum.at/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
RUN tar xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt/hadoop
RUN rm hadoop-${HADOOP_VERSION}.tar.gz

# Install Spark without hadoop, that is assumed to be installed separately (this to have native libraries in hadoop):
# https://spark.apache.org/docs/latest/hadoop-provided.html
RUN mkdir -p /opt/spark
RUN wget http://mirror.synyx.de/apache/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-without-hadoop.tgz
RUN tar xzf spark-${SPARK_VERSION}-bin-without-hadoop.tgz -C /opt/spark
RUN rm spark-${SPARK_VERSION}-bin-without-hadoop.tgz

# Install common Python packages for PySpark and data science
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# set env variables for Java, Spark, Hadoop and Python
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV SPARK_HOME /opt/spark/spark-${SPARK_VERSION}-bin-without-hadoop/
ENV HADOOP_HOME /opt/hadoop/hadoop-${HADOOP_VERSION}/

# Persist env variables and add /shared/docker/spark/init_env.sh to .bashrc.
# Script /shared/docker/spark/init_env.sh sources /env.sh and initializes a few more env variables.
RUN echo export JAVA_HOME=$JAVA_HOME > /env.sh
RUN echo export SPARK_HOME=$SPARK_HOME >> /env.sh
RUN echo export HADOOP_HOME=$HADOOP_HOME >> /env.sh
RUN echo source /shared/docker/spark/init_env.sh >> ~/.bashrc

# Setup Pseudo-Distributed Mode (YARN on single machine)
# https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html#YARN_on_a_Single_Node

# Setup SSH access
RUN passwd -d root
COPY id_rsa.pub /root/.ssh/authorized_keys
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 0600 /root/.ssh/id_rsa /root/.ssh/authorized_keys

# Setup HDFS and YARN
ADD etc/hadoop/* ${HADOOP_HOME}/etc/hadoop/

# Copy the spark conf file to the location where spark expects it:
ADD etc/spark/* ${SPARK_HOME}/conf/

# Add hadoop-env-init.sh contents (it sources /shared/docker/spark/init_env.sh) to beginning of hadoop-env.sh script
RUN cat ${HADOOP_HOME}/etc/hadoop/hadoop-env-init.sh ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh >/tmp/hadoop-env.sh && mv /tmp/hadoop-env.sh ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh
RUN rm ${HADOOP_HOME}/etc/hadoop/hadoop-env-init.sh && chmod +x ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# customise Jupyter setup with a few useful extensions
# RUN jupyter contrib nbextension install --user
RUN jupyter nbextension enable toc2/main # table of contents
RUN jupyter nbextension enable python-markdown/main # {{x}} in markdown cells gets rendered as the Python x variable
RUN jupyter nbextension enable code_prettify/autopep8 # help with PEP8 compliance
RUN jupyter nbextension enable execute_time/ExecuteTime # print execution time after each cell completes evaluation

# create kernel spec for scala
RUN python -m spylon_kernel install

# Add spark job progressbar integration for Jupyter notebook
# This does not work yet on Jupyter lab: https://github.com/mozilla/jupyter-spark/pull/41
RUN pip3 install jupyter-spark
RUN jupyter serverextension enable --py jupyter_spark
RUN jupyter nbextension install --py jupyter_spark
RUN jupyter nbextension enable --py jupyter_spark
RUN jupyter nbextension enable --py widgetsnbextension

# set default working directory
WORKDIR /data/notebooks
