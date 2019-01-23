from pyspark.sql.functions import *

from spark_helpers.spark_helpers import create_df
from pyspark.sql.types import StructType, IntegerType, StructField

def test_create_spark_dataframe():
    """
    Purpose of the test: verify that we can create a spark dataframe.
    Implicitly, it tests the availability of a Spark cluster.
    :return:
    """

    data = [1, 2, 3, 4, 5]

    df = create_df([[x] for x in data], StructType([StructField("Id", IntegerType(), True), ]))
    df.printSchema()

    # this triggers the materialisation of the dataframe on the driver
    df.show()
