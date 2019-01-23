import os
import tempfile
from pyspark import SparkConf

# get current active environment
active_profile = os.environ.get('PROFILE')

path_pkg = os.path.dirname(__file__)

app_name = "spark-app"
spark_conf = SparkConf()
spark_sys_properties = {}

if active_profile == 'profile_local':
    # Connect to this spark master node
    spark_master = 'spark://spark-master:7077'

    # Execute job n this deploy mode, could be 'client' or 'cluster'
    spark_conf.set('spark.submit.deployMode', 'client')

    # Timeout in seconds for the broadcast wait time in broadcast joins, in seconds
    spark_conf.set('spark.sql.broadcastTimeout', 36000)

    # number of cores to be used for each job
    spark_conf.set('spark.cores.max', 1)

    # Set location of Derby database in warehouse
    # https://spark.apache.org/docs/latest/sql-programming-guide.html#hive-tables
    spark_conf.set('spark.sql.warehouse.dir', '/tmp/spark-warehouse')

    # memory to be allocated for executor in Gb
    spark_sys_properties['spark.executor.memory'] = '1g'

    # memory to be allocated for executor in Gb
    spark_sys_properties['spark.driver.memory'] = '1g'

    # set session timezone to UTC
    spark_conf.set('spark.sql.session.timeZone', 'UTC')

elif active_profile == 'profile_server':
    spark_master = 'spark://spark-master:7077'
    spark_conf.set('spark.submit.deployMode', 'client')
    spark_conf.set('spark.sql.broadcastTimeout', 36000)
    spark_conf.set('spark.cores.max', 1)
    spark_conf.set('spark.sql.warehouse.dir', '/tmp/spark-warehouse')
    spark_sys_properties['spark.executor.memory'] = '40g'
    spark_sys_properties['spark.driver.memory'] = '40g'
    spark_conf.set('spark.sql.session.timeZone', 'UTC')
