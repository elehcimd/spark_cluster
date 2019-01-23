## Local cluster config

# SSH bridged port of Docker master node (defined also in docker-compose.yml)
master_ssh_port = 6022

# PySpark profile to consider
profile ='profile_local'

# Default directory on host mapped to /data
data_dir = './data'

## Remote cluster config

# hostname or address
srv_host = 'your-server-address'

# user
srv_user = 'your-username'

# keyfile to authenticate the user for SSH access
srv_keyfile = '~/.ssh/id_rsa'

# directory on remote server where to setup the Spark cluster
srv_dir = "/home/{srv_user}/spark_cluster".format(srv_user=srv_user)

