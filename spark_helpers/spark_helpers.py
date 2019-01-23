# Imports

import os
import shutil
import tempfile
from IPython.display import display
from copy import copy
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import *
from pyspark.sql.types import *

from .spark_config import app_name, path_pkg
from .spark_config import spark_conf, spark_master, spark_sys_properties


class SparkClusterException(Exception):
    """
    Raised if not possible to instantiate Spark handler from driver
    """
    pass


def show(r, n=3):
    """
    Display nicely a PySpark dataframe in jupyter notebook
    :param r: dataframe
    :param n: number of rows to display
    :return:
    """
    display(r.limit(n).toPandas())


def get_pathname():
    """
    Retrieve the pathname of this module.
    :return: string - path to this module
    """

    path_elems = path_pkg.split('/')[0:-1]
    return '/'.join(path_elems)


def create_spark_sql_context(app_name):
    """
    Instantiates spark and sql contexts.
    If executed twice, it will return the first instance.

    :param app_name: name of the app to assign to the created spark context.
    :return:
    """
    # Initialize Spark and SQL context

    # set spark config and master
    conf = copy(spark_conf)
    conf.setMaster(spark_master).setAppName(app_name)

    # set PROFILE environment in executors
    conf.setExecutorEnv('PROFILE', os.environ.get('PROFILE'))

    # set spark system properties
    for k, v in spark_sys_properties.items():
        SparkContext.setSystemProperty(k, v)

    sc = SparkContext(conf=conf)

    if sc is None:
        raise SparkClusterException("Unable to instantiate SparkContext")

    # Adding spark_helpers.zip to SparkContext so that workers can load modules from spark_helpers
    # http://apache-spark-user-list.1001560.n3.nabble.com/Loading-Python-libraries-into-Spark-td7059.html
    tmp_dir = tempfile.mkdtemp()
    sc.addPyFile(
        shutil.make_archive(base_name='{}/spark_cluster_pkg'.format(tmp_dir), format='zip',
                            root_dir=os.path.abspath(path_pkg)))

    sq = SQLContext(sc)

    if sq is None:
        raise SparkClusterException("Unable to instantiate SQLContext")

    return sc, sq


class SparkSqlContext:
    """
    Singleton that manages pyspark and sql contexts.
    In the future, it can be extended to support the creation of CassandraSparkContext.
    """

    sc = None
    sq = None

    @classmethod
    def setup(cls, app_name=app_name):
        """
        Create Spark and Sql contexts
        :param app_name: spark application name
        :return: pair (sc:SparkContext, sq:SQLContext)
        """
        if not cls.sc:
            cls.sc, cls.sq = create_spark_sql_context(app_name)

        return cls.sc, cls.sq


def create_df(*args, **kwargs):
    """
    Helper function that creates a Spark DataFrame given rows and schema.
    :param args: positional arguments of createDataFrame
    :param kwargs: optional arguments of createDataFrame
    :return: dataframe
    """
    (sp, sq) = SparkSqlContext.setup()
    return sq.createDataFrame(*args, **kwargs)


def read_df():
    """
    Helper function that returns a dataframe reader object, can be used to
    read CSV and Parquet files.
    :return: PySpark DataFrame reader object
    """
    (sp, sq) = SparkSqlContext.setup()
    return sq.read
