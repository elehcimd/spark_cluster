import fabric
import multiprocessing
import os
from fabric.api import local, settings
from fabric.decorators import task
from time import sleep

from config import master_ssh_port, data_dir, profile, srv_host, srv_user, srv_keyfile, srv_dir

# disable "Done." output
fabric.state.output.status = False

# These variables are overwritten immediately by /shared/init_env.sh , that is considered
# at containers creation with "fab start_cluster". For all other commands, these variables
# are set to avoid "variable is undefined" warnings, even though their values are not considered.
default_env = "PROFILE=dummy DATA_DIR=./data"

# Change directory to directory containing this script
os.chdir(os.path.abspath(os.path.dirname(__file__)))


class AbortException(Exception):
    """
    Exception triggered if containers creation fails
    """
    pass


def timeit(f):
    """
    Log execution time of function
    :param f: function
    :return: none
    """

    def timed(*args, **kw):
        """
        Measure execution time for function
        """
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('[elapsed_time={}s]'.format(int(te - ts)))
        return result

    return timed


def docker_exec(cmd):
    """
    Execute command in spark-driver container
    :param cmd: command to be executed
    :return:
    """

    local('{default_env} docker-compose exec {service} /bin/bash -i -c "{cmd}"'.format(default_env=default_env,
                                                                                       service="spark-driver", cmd=cmd))


@task
def build(params=""):
    """
    Stop containers (if running) and build image
    :return: none
    """

    local('{default_env} docker-compose stop'.format(default_env=default_env))
    local('{default_env} docker-compose build {params}'.format(default_env=default_env, params=params))


@task
def logs():
    """
    Print live stdout/stderr from Docker containers
    :return:
    """
    local('{default_env} docker-compose logs -f'.format(default_env=default_env))


@task
def kill():
    """
    Terminate containers as fast as possible, might cause corrupted files in the /data directory
    """

    local('{default_env} docker-compose kill'.format(default_env=default_env))


@task
def stop():
    """
    Terminate Docker containers nicely and cleanly
    """

    # `kill` would be faster, but doesnt play nicely with HDFS
    local('{default_env} docker-compose stop'.format(default_env=default_env))


@task
def ps():
    """
    List active containers
    """

    local('{default_env} docker-compose ps'.format(default_env=default_env))


@task
def start(profile=profile, data_dir=data_dir, n_cores=1):
    """
    Start Docker containers: spark-master, spark-slave(s), spark-driver
    :n_cores: number of replicates for spark-slave docker. 0 means number of CPU cores, default is 1.
    :return: none
    """

    if n_cores == "0":
        n_cores = multiprocessing.cpu_count()

    print(
        "Starting Docker containers with params: profile={profile} data_dir={data_dir} n_cores={n_cores}".format(
            profile=profile,
            data_dir=data_dir,
            n_cores=n_cores))

    stop()

    with settings(abort_exception=AbortException):
        try:

            # We recreate the container from a clean image with --force-recreate, in background with --detach,
            # with n_cores instances of spark-slave containers (by default, 1)
            local(
                'PROFILE={profile} DATA_DIR={data_dir} docker-compose up --detach --force-recreate --scale spark-slave={n_cores}'.format(
                    profile=profile,
                    data_dir=data_dir,
                    n_cores=n_cores))
        except (AbortException, KeyboardInterrupt, Exception) as e:
            stop()
            print('Debug errors with $ fab docker_logs')

    print("Spark cluster up and running!")


@task
def shell(service="spark-driver", cmd='/bin/bash'):
    """
    Open shell on docker-driver container
    :param service:
    :return:
    """
    local('{default_env} docker-compose exec {service} {cmd}'.format(default_env=default_env, service=service, cmd=cmd))


@task
def test_pep8():
    """
    Run only pep8 test
    :return:
    """

    docker_exec('py.test /shared/tests/test_pep8.py')


@task
def test(params=''):
    """
    Run all tests
    :param params: parameters to py.test
    :return:
    """

    docker_exec('py.test /shared/tests {}'.format(params))


@task
def test_sx(params=''):
    """
    Run all tests printing output and terminating tests at first failure
    :param params: parameters to py.test
    :return:
    """

    docker_exec('py.test -sx /shared/tests {}'.format(params))


@task
def fix_pep8():
    """
    Fix a few common and easy-to-fix PEP8 mistakes
    :return:
    """

    docker_exec(
        'autopep8 --select E251,E303,W293,W291,W391 --aggressive --in-place --recursive {}'.format('.'))


@task
def tunnel(host="localhost"):
    """
    Create SSH port forwarding tunnel from localhost to spark-driver container network
    """
    cmd = 'ssh -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i docker/spark/id_rsa -p {master_ssh_port} root@{host} -ND 9000'.format(
        host=host, master_ssh_port=master_ssh_port)

    while True:
        # this makes sure that the tunnel is kept open if we restart the cluster or if the network becomes temporarily not reachable
        with settings(warn_only=True):
            local(cmd)
            sleep(1)


@task
def generate_ssh_keys():
    """
    Generate SSH key pair to be used within cluster and to SSH into the spark-master container
    :return:
    """
    local('ssh-keygen -b 2048 -t rsa -f docker/spark/id_rsa -q -N ""')
    local('chmod 0600 docker/spark/id_rsa*')


@task
def ssh_master(host="localhost"):
    """
    SSH into the spark-master Docker container
    :param host: host where the container is running
    :return:
    """
    local(
        "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i docker/spark/id_rsa -p {master_ssh_port} root@{host}".format(
            host=host, master_ssh_port=master_ssh_port))


# The following tasks are useful to manage the remote instance of the cluster

@task
def ssh(host=srv_host):
    """
    SSH to remote server
    :param host: hostname or address of server
    :return:
    """
    local(
        'ssh -i {srv_keyfile} {srv_user}@{srv_host}'.format(srv_keyfile=srv_keyfile, srv_user=srv_user, srv_host=host))


@task
def rsync(host=srv_host):
    """
    Synchronise local spark_cluster directory to remote server
    All extra files are deleted and modifications are overwritten.
    Files in .gitignore are ignored in the synchronisation. To delete them on remote host, add rsync parameter "--delete-excluded".
    :param host: hostname or address of server
    :return:
    """
    local(
        "ssh {srv_user}@{srv_host} sudo chown -R {srv_user}:{srv_user} {srv_dir}".format(srv_user=srv_user,
                                                                                         srv_host=host,
                                                                                         srv_dir=srv_dir))
    local(
        "rsync -arvz --progress --exclude-from=.gitignore --delete -e ssh . {srv_user}@{srv_host}:{srv_dir}".format(
            srv_user=srv_user, srv_host=host, srv_dir=srv_dir))


@task
def copy_keys():
    """
    Copy local SSH keys to server host
    :return:
    """
    local("scp docker/spark/id_rsa* {srv_user}@{srv_host}:{srv_dir}/docker/spark/".format(srv_user=srv_user,
                                                                                          srv_dir=srv_dir,
                                                                                          srv_host=srv_host))
