# Containerized Spark cluster for Data Science with Jupyter for both Python and Scala

This project lets you create a Spark cluster based on `ubuntu:18.04`, `OpenJDK 8`, `Spark 2.4.5`, `Hadoop 2.8.5`, `Python 3.6` in a few easy steps. Highlights:

* Python `3.6` by default
* It creates three Docker containers based on the same image: `spark-master`, `spark-slave`, and `spark-driver`
* PySpark jobs are executed on the `spark-driver` container in client mode
* The `spark-driver` container provides a `Jupyter` web interface to the cluster, altogether with `PySpark` helper functions and demo notebooks for Python+Spark and Scala+Spark
* The `HDFS` filesystem and the `notebooks` directory are persisted in the host-mapped `/data` directory
* It matches the setup of AWS EMR version `emr-5.28.1` (this uses Spark 2.4.4, we're already on 2.4.5)
* Python packages for data science and AWS integration already installed: `numpy`, `scipy`, `pandas`, `matplotlib`, `jupyterlab`, `boto3`, `awscli`, `s3fs`
* Jupyter extensions enabled by default: `jupyter-spark`, `toc2`, `python-markdown`, `code_prettify`, `execute_time`

## Creating a Python environment on MacOS

Install pyenv:

```
brew update
brew install pyenv
brew install pyenv-virtualenv
```

Add to `~.zshrc`:

```
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
  export PYENV_VIRTUALENV_DISABLE_PROMPT=1
fi

if which pyenv-virtualenv-init > /dev/null; then eval "$(pyenv virtualenv-init -)"; fi
```

Create environment:

```
pyenv virtualenv 3.6.10 spark_cluster
pyenv activate spark_cluster
pip install Fabric3==1.14.post1
```

## Managing a local instance of the cluster

The cluster runs on Docker containers orchestrated with `docker-compose`. All tasks are automated using Fabric.
Provide at least `4 Gb` of memory to the Docker engine: `"Preferences" > "Advanced" > "Memory"`
These steps apply to both Linux and MacOS environments, and let you build, start and stop the cluster:

1. Install `docker`: https://docs.docker.com/install/
2. Install `docker-compose`: https://docs.docker.com/compose/install/
3. Install the `Fabric3` Python package: `pip install Fabric3==1.14.post1`
4. Generate a SSH key pair with the command `fab generate_ssh_keys`
5. Build Docker image: `fab build`
6. Start cluster: `fab start`
7. Stop cluster: `fab stop`

> In Linux, you might need to add your user to the `docker` group to be able to execute `docker` commands: `sudo gpasswd -a $USER docker ; newgrp docker`

> To remove all existing Docker images and caches: `docker system prune -a`

PySpark configuration profiles are defined in `spark_cluster/spark_cluster/config.py` and define the PySpark configuration.
By default, two profiles are defined: `profile_local` and `profile_server`. You can add more, depending on your needs and environment(s). 
Changes to the `spark_cluster` Python package on the host are immediately reflected inside the `spark-driver` container, including the contents of `spark_config.py`.

By default, the cluster starts using the `"profile_local"` PySpark configuration profile and `./data` as `/data` directory. These default values can be changed in `config.py`.
You can start the cluster specifying different parameter values as follows:

```
fab start:profile=profile_server,data_dir=/data/spark_cluster
```

## Accessing the cluster

Web access to the cluster is handled with FoxyProxy: 

1. Install FoxyProxy plugin in your browser
2. Import `foxyproxy-settings.xml` from FoxyProxy
3. Activate proxy configuration
4. Start SSH tunnel: `fab tunnel`

You can now access these web services inside the cluster (make sure to start the tunnel first with `fab tunnel`):

* Jupyter lab: http://spark-driver:8888/lab
* Jupyter notebook: http://spark-driver:8888/tree
* Spark monitoring dashboard: http://spark-master:8080
* Hadoop monitoring dashboard: http://spark-master:8088/cluster
* HDFS monitoring dashboard: http://spark-master:50070/explorer.html

To SSH into the master node: `fab ssh_master`.

## Managing an additional remote instance of the cluster

In some situations, you might want to have a local cluster to experiment quickly and a remote cluster for bigger experiments.
The following steps let you manage faster the additional remote instance.

1. Configure the access to the remote host by editing the variables `srv_*` in the `config.py` file 
2. SSH into remote server with `fab ssh` and create the destination directory as specified by the `srv_dir` config variable
3. Sync the `spark_cluster` directory to the remote server: `fab rsync`
4. Copy SSH keys from local cluster setup to remote server: `fab copy_keys`
5. SSH into remote server with `fab ssh` and start the cluster with `fab start` 

You can access the web dashboards and Jupyter on the remote cluster by specifying a custom host/address `XYZ` for the SSH tunnel: `fab tunnel:XYZ`.
The same applies to access the remote Spark master node:`fab ssh_master:XYZ`.


## Fabric management tasks

The following `fab` tasks are defined:

* build: stop containers (if running) and build image
* `copy_keys`: copy local SSH keys to server host
* `fix_pep8`: fix a few common and easy-to-fix PEP8 mistakes
* `generate_ssh_keys`: generate SSH key pair to be used within cluster and to SSH into the spark-master container
* `kill`: terminate containers as fast as possible, might cause corrupted files in the /data directory
* `logs`: print live stdout/stderr from Docker containers
* `ps`: list active containers
* `rsync`: synchronise local spark_cluster directory to remote server
* `shell`: open shell on docker-driver container
* `ssh`: ssh into remote server
* `ssh_master`: ssh into the spark-master Docker container
* `start`: start Docker containers: spark-master, spark-slave(s), spark-driver
* `stop`: terminate Docker containers nicely and cleanly
* `test`: run all tests
* `test_pep8`: run only pep8 test
* `test_sx`: run all tests printing output and terminating tests at first failure
* `tunnel`: create SSH port forwarding tunnel from localhost to spark-driver container network

## Accessing HDFS from command line

You can access the HDFS filesystem from any container. Examples:

* Copy file to rood directory: `hdfs dfs -put /shared/README.md /`
* List contents of root directory: `hdfs dfs -ls /`
* Remove directory: `hdfs dfs -rm -r /out/`
* Move directory: `hdfs dfs -mv /out /data`

## Example of PySpark usage

The following code demonstrates:

* How to add a directory to `PYTHONPATH` to load your own packages
* How to create PySpark dataframes
* How to perform a join

```
# Add directory of spark_cluster repository, containing spark_cluster Python package
import sys
sys.path = ["/shared"] + sys.path

# Imports
from random import randint
from pyspark.sql import Row
from spark_helpers.spark_helpers import create_df

# Create two dataframes and join them
N = 10000

df1 = create_df([Row(id=randint(0, N-1)) for i in range(N)])
df2 = create_df([Row(id=randint(0, N-1)) for i in range(N)])

df1.join(df2, df1.id == df2.id).distinct().count() 
```

This example is also included in the included notebook demo.

## Execution flow

* Docker image: `docker/spark` defines the image for containers `spark-master`, `spark-slave`, and `spark-driver`
* Container entrypoints, dependencies, and health checks are defined in `docker-compose.yml`: `spark-driver` depends on `spark-slave` and `spark-master`, `spark-slave` depends on `spark-master`
* Entrypoints differentiate the behavior of the containers and are defined in `docker/spark/entrypoint_*.sh` scripts
* Entrypoints initialize the required environmental variables sourcing `/shared/docker/spark/init_env.sh` before starting their services: `dfs`, `yarn`, `spark`, and `jupyter`
* Script `init_env.sh` sources Spark, Hadoop and Python paths from `/env.sh`, built during the construction of the image


### Running the tests

Tests verify the PEP8 compliance of the Python code and the correct functioning of HDFS and Spark.
Tests are executed inside the `spark-driver` container. 

To run all tests, ignoring some innocuous "RuntimeWarning: numpy.dtype size changed" warnings:

```
fab test:--disable-pytest-warnings
```

To run tests printing output and stopping at first error:

```
fab test_sx
```

To run the pep8 test:

```
fab test_pep8
```

To fix some common pep8 errors in the code:

```
fab fix_pep8
```


## Credits and license

The spark_cluster project is released under the MIT license. Please see [LICENSE.txt](https://github.com/minodes/spark_cluster/blob/master/LICENSE.txt).

Contributors include:

* Michele Dallachiesa: https://github.com/elehcimd


## Contributing

1. Fork it
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Create a new Pull Request

