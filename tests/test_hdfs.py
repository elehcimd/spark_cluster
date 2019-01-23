from fabric.api import local

def test_hdfs():
    """
    Test connection to HDFS
    :return:
    """

    local("hdfs dfs -ls /")
