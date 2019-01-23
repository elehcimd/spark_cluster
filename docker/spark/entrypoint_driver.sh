#!/bin/bash

# Initialise environment profile and container name
echo "export PROFILE=$PROFILE CONTAINER_NAME=$CONTAINER_NAME" >>/root/.bashrc

# Initialize env variables
source /shared/docker/spark/init_env.sh

# Create notebooks folder if missing
mkdir -p /data/notebooks

# link container root directory to make it accessible from Jupyter lab
test ! -d /data/notebooks/root && ln -s / /data/notebooks/root

# Start Jupyter
jupyter lab --config=/shared/docker/spark/jupyter_notebook_config.py

