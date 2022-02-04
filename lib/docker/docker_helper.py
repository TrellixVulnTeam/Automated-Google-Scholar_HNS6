'''
A set of helper functions for working with the Docker program
    see:
    https://www.docker.com/
'''

import lib.logging as logging
LOG = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Init
#-------------------------------------------------------------------------------

def is_docker_ready(): return _is_docker_ready()

def _is_docker_ready():
    '''
    Check to see if docker is installed and running
    if not then throw to the caller
    '''
    if not _is_command_present():
        _exp = "Could not find the docker executable."
        _exp += "Docker needs to be installed for this to work."
        from lib.exceptions import docker
        raise docker.Could_not_find_executable(_exp) from None

    if not _is_running():
        _exp = "Docker is required. Startup Docker to continue."
        from lib.exceptions import docker
        raise docker.Docker_is_not_running(_exp) from None

    return True

def _is_command_present():
    '''
    Check if we can issue commands to the docker cli
    '''
    import shutil
    _docker_path = shutil.which("docker")

    if _docker_path is None:
        return False

    from pathlib import Path
    _docker_path = Path(_docker_path)

    if not _docker_path.exists():
        return False

    return True

'''
NOTE
here the docker library puts out an ugly chained exception when DockerException
is raise
so we supress that with the formulation:
    raise Docker_is_not_running(_exp) from None
which suppresses the context for the exception
    see:
    https://stackoverflow.com/questions/24752395/python-raise-from-usage
    https://www.python.org/dev/peps/pep-0409/
'''
def _is_running():
    '''
    Check if the Docker client is running, and if it isn't raise an exception
    '''
    LOG.debug(f"Checking if Docker is running.")
    import docker
    from docker.errors import DockerException
    #see: https://docker-py.readthedocs.io/en/stable/index.html
    try:
        docker.from_env()
        LOG.debug(f"Docker is running.")
        return True
    except DockerException:
        LOG.debug(f"Docker is NOT running.")
        return False

#-------------------------------------------------------------------------------
#Client
#-------------------------------------------------------------------------------

def get_client(): return _get_client()

def _get_client():
    _is_docker_ready()

    import docker
    return docker.from_env()

#-------------------------------------------------------------------------------
#Containers
#-------------------------------------------------------------------------------

def list_containers():
    '''
    BUG
    occasionally client.containers.list() will throw nonsense exceptions like:
        for _container in client.containers.list():
        docker.errors.NotFound: 404 Client Error for
        http+docker://localnpipe/v1.41/containers/16d183c9e6f50fa570e430ec6a
        cf6411d2013b1321dab45dd455c0f7fcd5deb4/json: Not Found
        ("No such container: 
        16d183c9e6f50fa570e430ec6acf6411d2013b1321dab45dd455c0f7fcd5deb4")
    (listing containers should not access them?)

    and all docker exceptions are (annoyingly) not derived from a single
    base exception class

    so instead, we have to inspect any exception and see if it's from
    docker.errors and ignore them by returning an empty list
        see:
        https://stackoverflow.com/questions/14206804/catch-all-exceptions-from-an-imported-module
        https://stackoverflow.com/questions/56636412/catching-all-of-modules-exceptions
        https://stackoverflow.com/questions/32536983/pythonic-way-to-catch-all-exceptions-from-a-module
    '''
    _f = {"status": "running"}
    _client = _get_client()
    try:
        _containers_seen_from_docker = _client.containers.list(filters=_f)
    except Exception as e:
        if "docker.errors" in str(type(e)):
            _containers_seen_from_docker = []
        else:
            raise

    return _containers_seen_from_docker

#-------------------------------------------------------------------------------
# Swarm
#-------------------------------------------------------------------------------

def in_swarm(): return _in_swarm()

def init_swarm(): return _init_swarm()

def _in_swarm():
    LOG.debug("Checking if docker is running as part of a swarm.")

    _is_docker_ready()

    import docker
    client = docker.from_env()

    LOG.debug("Raw swarm information:")
    LOG.debug(client.swarm.attrs)
    LOG.debug(len(client.swarm.attrs))

    return (len(client.swarm.attrs) != 0)

def _init_swarm():
    _is_docker_ready()

    if not _in_swarm():
        import docker
        client = docker.from_env()
        client.swarm.init()

def list_services(): return _list_services()

def _list_services():
    client = _get_client()
    
    return [_s for _s in client.services.list()]

def _remove_all_services():
    for _s in _list_services():
        _s.remove()