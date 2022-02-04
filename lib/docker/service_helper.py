import lib.logging as logging
LOG = logging.getLogger(__name__)

'''
TODO
breakup _start() into a pipeline that calls several other functions to modify
the docker command string iteratively before passing it to subprocess.run()
'''
class _Service_Helper:
    '''
    This class acts as an object that manages a single service on a docker swarm
        see:
        https://docs.docker.com/engine/swarm/services/
    '''
    def __init__(self, image, **kwargs):
        self._docker_image = self._check_image_arg(image)
        self._service = None #keep track of the service object

        self._kwargs = {}
        self._kwargs['replicas'] = 1

        if 'replicas' in kwargs:
            self._kwargs['replicas'] = self._replicas(kwargs['replicas'])

        self._kwargs['mounts'] = []
        self._kwargs['environment_variables'] = []
        self._kwargs['port_mappings'] = []

    def _check_image_arg(self, _img):
        import lib.docker.image_helper as IH
        return IH.get_latest_image(self._check_for_image_name(_img))

    def start(self):
        import lib.docker.docker_helper as DH
        DH.is_docker_ready()

        if not DH.in_swarm():
            DH.init_swarm()

        self._start()

    def _start(self):
        '''
        Startup the service as configured on the object
        '''

        '''
        BUG
        the docker library handles the --mount option poorly
        so instead, we pass commands to docker manually when creating services
            we have to use subprocess.run rather than the library calls
        '''        
        _cmd = f'docker service create'

        #name the new service with a unique name so we can locate the
        #the service object after creation
        import uuid
        _name = str(uuid.uuid4())

        _cmd += " "
        _cmd += f"--name {_name}"

        _cmd += " "
        _cmd += f"--replicas {self._kwargs['replicas']}"

        _mounts = self._mount()
        if len(_mounts) > 0:
            _m_str = ""
            for _m in _mounts:
                _m_str += f'--mount "type=bind,source={_m["source"]},destination={_m["destination"]}" '

            _cmd += " "
            _cmd += _m_str

        _env_vars = self._environment()
        if len(_env_vars) > 0:
            _env_str = ""
            for _item in _env_vars:
                #KEY=value
                _env_str += f"--env {list(_item.keys())[0]}={list(_item.values())[0]} "
            
            _cmd += " "
            _cmd += _env_str

        _publish_ports = self._publish()
        if len(_publish_ports) > 0:
            _pub_str = ""
            for _item in _publish_ports:
                #external_port:swarm_port
                _pub_str += f"--publish {list(_item.keys())[0]}:{list(_item.values())[0]} "
            
            _cmd += " "
            _cmd += _pub_str

        _cmd += " "
        _cmd += str(self._docker_image)
        
        import subprocess
        _ret = subprocess.run(_cmd, capture_output=True)

        if _ret.returncode != 0:
            import lib.exceptions as exp
            raise exp.Could_not_launch_service(f"Docker returned: {_ret}")

        #then find the newly launched service
        import lib.docker.docker_helper as DH
        for _s in DH.list_services():
            if _s.name == _name:
                self._service = _s
                break
        else:
            import lib.exceptions as exp
            _m = f"Could not find service, though Docker claimed it launched."
            raise exp.Could_not_launch_service(_m)

        #then wait for the replicas to come online
        import lib.util as util
        util.wait_for( self._is_synchronized )

    def _container_ids(self):
        '''
        return a list of container ids associated with the service
        '''
        LOG.debug("Checking for container IDs assocaited with this service")

        '''
        The docker client handles containers associated with services oddly
        It will list containers, but not all containers are associated with
        a service
        It will list tasks associated with a service
        (which are nominally containers)
        but sometimes include tasks that are associated with no container?
        And sometimes there can be tasks running while no containers are present
        at all
        The solution then is match the containers by ID that are associated
        with the service
        '''
        if not self._is_running():
            return []

        import lib.docker.docker_helper as DH
        _containers = []
        for _container in DH.list_containers():
            _containers.append(_container.id)

        _tasks = []
        for _task in self._service.tasks():
            #check the task dict for information about their associated container
            #not all keys in the task dict are present at all times
            #so doing short-circuit evaluation to test for them
            #and sometimes the container ids can be empty, so skipping those
            if ("Status" in _task) and ("ContainerStatus" in _task["Status"]) \
            and ("ContainerID" in _task["Status"]["ContainerStatus"]):
                if len(_task["Status"]["ContainerStatus"]["ContainerID"]) != 0:
                    _id = _task["Status"]["ContainerStatus"]["ContainerID"]
                    _tasks.append(_id)

        _tasks = set(_tasks)
        _containers = set(_containers)

        return list( _tasks & _containers )

    def _is_synchronized(self):
        '''
        Check if the number of observed containers matches the number of
        configured replicas
        '''
        LOG.debug("Checking for all containers to appear.")

        LOG.debug("Container IDs:")
        _ids = self._container_ids()
        LOG.debug(_ids)

        LOG.debug("Target number of IDs:")
        LOG.debug(self._kwargs['replicas'])

        return (len(_ids) == self._kwargs['replicas'])

    def stop(self):
        '''
        Stop the service on the swarm and cleanup all containers on the swarm
        '''
        if not self._is_running():
            return

        self._service.remove()

        self._service = None

    def is_running(self): return self._is_running()
    
    def _is_running(self):
        if self._service is None:
            return False

        import lib.docker.docker_helper as DH
        try:
            DH.is_docker_ready()
        except:
            return False

        import docker
        client = docker.from_env()

        for _s in client.services.list():
            if _s.id == self._service.id:
                return True
        
        return False
    
    def image(self, img=None): return self._image(img)

    def _image(self, img=None):
        '''
        set/get the image assocaited with the service
        if called with no arguments, returns the current image or None
        if called with arguments, sets image associated with this service to
        it and returns the image
        '''
        if not img is None:
            self._docker_image = self._check_image_arg(img)

        return self._docker_image

    def _check_for_image_name(self, _img):
        if not isinstance(_img, str):
            import lib.exceptions
            raise lib.exceptions.Bad_argument("Argument should be string")

        if len(_img) == 0:
            import lib.exceptions
            raise lib.exceptions.Bad_argument("Argument should be name of an image.")

        return _img

    def _replicas(self, num=None):
        '''
        set/get the number of instances configured for the service
        if called with no arguments, returns the number of replicas
        if called with arguments, sets the number of replicas to that number
        '''
        if not num is None:
            import lib.util as util
            if not util.is_int(num):
                import lib.exceptions
                _m = "Argument 'replicas' should be integer."
                raise lib.exceptions.Bad_argument(_m)

            _r = int(num)

            if _r < 1:
                import lib.exceptions
                _m = "Argument 'replicas' should be >= 1."
                raise lib.exceptions.Bad_argument(_m)

            self._kwargs['replicas'] = _r

        return self._kwargs['replicas']

    def containers(self):
        import lib.docker.docker_helper as DH
        DH.is_docker_ready()

        if not self._is_running():
            return []

        _ids = self._container_ids()

        _ret = []
        for _id in _ids:
            import lib.docker.container_helper as CH
            import lib.exceptions as exp
            try:
                _ret.append( CH.get_container(_id) )
            except exp.docker.No_such_container:
                pass
        return _ret

    def mount(self, src=None, dst=None):
        '''
        Setup a bind mount to be shared by the tasks in the service
        With no arguments, just lists current mounts attached to the service
        The mounts are applied when the service is started
        '''
        if (src is None) and (dst is None):
            return self._mount()

        if ((src is None) and (not dst is None)):
            import lib.exceptions as exp
            _m = "If source is defined, then we need a destination"
            raise exp.Bad_argument(_m)

        if ((not src is None) and (dst is None)):
            import lib.exceptions as exp
            _m = "If destination is defined, then we need a source"
            raise exp.Bad_argument(_m)

        from pathlib import Path
        if not Path(src).exists():
            import lib.exceptions as exp
            _m = f"Source should be valid path; Instead saw: {src}"
            raise exp.Bad_argument(_m)

        if not isinstance(dst, str):
            import lib.exceptions as exp
            _m = f"Need a path string for the destination"
            raise exp.Bad_argument(_m)

        '''
        On Windows the Docker Client has an EXTREMELY hard time with Windows
        paths
        so a fix is to convert windows paths into the shortened 8.3 (DOS) form
        and use that
        As that process factors out some of the more difficult to manage parts
        of Windows paths
            e.g. spaces, special characters, etc.
        '''
        _src = src
        import platform
        if platform.system() == 'Windows':
            import lib.util
            _src = lib.util.get_short_path_name(src)

            if _src is None:
                import lib.exceptions as exp
                _m = "There was an issue converting this Windows Path "
                _m += "into a short (8.3) format for use with docker."
                _m += "Cannot continue, giving up."
                raise exp.Bad_argument(_m)

        return self._mount(_src, dst)

    def _mount(self, src=None, dst=None):
        if (src is None) and (dst is None):
            return self._kwargs['mounts']

        self._kwargs['mounts'].append({
            "source": src,
            "destination": dst,
            })

        return self._kwargs['mounts']

    def _require_manual_commands(self):
        return (len(self._kwargs['mounts']) > 0)

    def environment(self, key=None, value=None):
        if ((key is None) and (not value is None)):
            import lib.exceptions as exp
            _m = "If key is defined, then we need a value."
            raise exp.Bad_argument(_m)

        if ((not key is None) and (value is None)):
            import lib.exceptions as exp
            _m = "If value is defined, then we need a key."
            raise exp.Bad_argument(_m)

        return self._environment(key, value)

    def _environment(self, key=None, value=None):
        if not ((key is None) and (value is None)):
            _env = {str(key):str(value)}
            self._kwargs['environment_variables'].append( _env )

        return self._kwargs['environment_variables']

    def publish(self, published=None, target=None):
        if ((published is None) and (not target is None)):
            import lib.exceptions as exp
            _m = "If `published` is defined, then we need a port to map it to."
            raise exp.Bad_argument(_m)

        if ((not published is None) and (target is None)):
            import lib.exceptions as exp
            _m = "If `target` is defined, then we need an external port to map it to."
            raise exp.Bad_argument(_m)

        if not ((published is None) and (target is None)):
            for _port in [published, target]:
                import lib.util as util
                if not util.is_int(_port):
                    import lib.exceptions as exp
                    _m = f"This value should be an integer: {_port}"
                    raise exp.Bad_argument(_m)

                if not (0 <= _port <= 65535):
                    import lib.exceptions as exp
                    _m = f"Bad port definition, should be in the range of: 0 to 65535"
                    raise exp.Bad_argument(_m)

        return self._publish(published, target)

    def _publish(self, published=None, target=None):
        if not ((published is None) and (target is None)):
            _env = {str(published):str(target)}
            self._kwargs['port_mappings'].append( _env )

        return self._kwargs['port_mappings']