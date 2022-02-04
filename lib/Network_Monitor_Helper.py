import lib.logging as logging
LOG = logging.getLogger(__name__)

class Network_Monitor_Helper:
    def __init__(self):
        self._service = None
        self._container = None
        self._start_time = None
        self._stop_time = None
        self._tmp_log_dir = None

    def _setup(self):
        from lib.docker.service_helper import _Service_Helper as SH
        _sh = SH("network_monitor")

        from pathlib import Path
        _service_share = Path("./lib/service_share/network_monitor_worker")
        _sh.mount(_service_share, "/home/headless")
        
        from pathlib import Path
        _lib = Path("./lib/")
        _sh.mount(_lib, "/home/headless/lib")

        #BUG
        #as we use a temporary folder here for the log directory inside the
        #container, we have to store the object related to the temporary
        #directory for as long as the life of the service
        #otherwise the temporary directory will remove itself and cause
        #issues with docker and the software in the container
        #see: https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory
        #thus we store it on self and trigger its cleanup() on teardown and
        #only dispose of the object then
        import tempfile
        self._tmp_log_dir = tempfile.TemporaryDirectory()

        from pathlib import Path
        _log_dir = Path(self._tmp_log_dir.name)
        _sh.mount(_log_dir, "/home/headless/log")

        _sh.start()
        
        return _sh

    def _teardown(self):
        self._service.stop()
        self._service = None
        self._container = None
        self._start_time = None
        self._stop_time = None
        
        if not self._tmp_log_dir is None:
            self._tmp_log_dir.cleanup()
        
        del self._tmp_log_dir
        self._tmp_log_dir = None

    def _is_running(self):
        if (self._service is None) or (self._container is None):
            return False
        return True

    def _start_monitoring(self, container):
        container.exec("python3 /home/headless/start_monitoring.py")

    def _was_up(self, container, start, stop):
        kwargs = {'stdout': True, 'stderr': True, 'detach':False}
        cmd = f"python3 /home/headless/was_up.py {start} {stop}"
        res = container.exec(cmd, **kwargs)

        import json
        return json.loads( res.output.decode().strip() )

    def start(self):
        if self._is_running(): return

        self._service = self._setup()
        self._container = self._service.containers()[0]
        self._start_monitoring(self._container)

        import time
        self._start_time = time.time()

        return self._start_time

    def stop(self): return self._stop(self._container, self._start_time)

    def _stop(self, container, start):
        if not self._is_running(): return

        import time
        self._stop_time = time.time()

        res = self._was_up(container, start, self._stop_time)

        self._teardown()

        return res