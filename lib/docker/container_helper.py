import lib.logging as logging
LOG = logging.getLogger(__name__)

def get_container(_id): return _Container_Helper(_id)

class _Container_Helper:
    def __init__(self, _id):
        self._id = _id
        self._container = self._get_container(self._id)

    def _get_container(self, _id):
        import lib.docker.docker_helper as DH
        client = DH.get_client()

        import docker.errors
        import lib.exceptions as exc
        try:
            return client.containers.get(_id)
        except docker.errors.NotFound:
            raise exc.docker.No_such_container(f"Container not found: {_id}")

    def is_running(self): return self._is_running()

    def _is_running(self):
        import lib.docker.docker_helper as DH
        for _c in DH.list_containers():
            if self._id == _c.id:
                return True
        return False

    def exec(self, command, **kwargs):
        if not self._is_running():
            import lib.exceptions as exp
            raise exp.docker.Container_not_running(self._id)

        _kwargs = {}
        _kwargs['stdout'] = False
        _kwargs['stderr'] = False
        _kwargs['detach'] = True

        if ('stdout' in kwargs) and not (isinstance(_kwargs['stdout'], bool)):
            import lib.exceptions as exp
            raise exp.Bad_argument("Argument 'stdout' should be bool.")

        if ('stderr' in kwargs) and not (isinstance(_kwargs['stderr'], bool)):
            import lib.exceptions as exp
            raise exp.Bad_argument("Argument 'stderr' should be bool.")

        if ('detach' in kwargs) and not (isinstance(_kwargs['detach'], bool)):
            import lib.exceptions as exp
            raise exp.Bad_argument("Argument 'detach' should be bool.")

        if ('stdout' in kwargs):
            _kwargs['stdout'] = kwargs['stdout']

        if ('stderr' in kwargs):
            _kwargs['stderr'] = kwargs['stderr']

        if ('detach' in kwargs):
            _kwargs['detach'] = kwargs['detach']

        return self._exec(command, **_kwargs)

    def _exec(self, command, **kwargs):
        return self._container.exec_run(command, **kwargs)

    def stop(self):
        '''
        Kill the underlying docker container
        '''
        if not self._is_running():
            return

        self._container.remove(force=True)

    def id(self):
        return self._container.id

    def restart(self, **kwargs):
        if not self._is_running():
            return

        self._container.restart(**kwargs)

    def cp_to(self, src, dst):
        for _p in [src, dst]:
            import lib.util as util
            if not util.is_pathlike(_p):
                import lib.exceptions as exp
                raise exp.Bad_argument(f"Argument `{_p}` should be a pathlike.")

        from pathlib import Path
        _src = Path(src)

        if not _src.exists():
            import lib.exceptions as exp
            raise exp.Bad_argument("Argument `src` should be a valid file.")

        return self._cp_to(_src, dst)

    def _cp_to(self, src, dst):
        if not self._is_running():
            return

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdirname:
            from pathlib import Path
            _tmpdir = Path(tmpdirname)

            import shutil
            _putfile = Path( shutil.copy(src, _tmpdir) )

            _tar_path = str(_tmpdir / "put.tar")
            #then creating a temporary tar file
            import tarfile
            with tarfile.open(_tar_path, "w") as tar:
                '''
                NOTE
                strange behaviour
                by default tar adds the entire absolute path to the file inside
                the tar archive
                so to avoid this behaviour, we use `arcname` to add the file
                as just the filename, instead of also the full path to the file
                '''
                tar.add(_putfile, arcname=_putfile.name)

            with open(_tar_path, "rb") as f:
                import docker
                try:
                    self._container.put_archive(dst, f)
                except docker.errors.NotFound:
                    m = f"No such path in container: {dst}"
                    import lib.exceptions as exp
                    raise exp.Bad_Path(m) from None

        return True