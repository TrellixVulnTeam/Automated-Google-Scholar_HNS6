import lib.logging as logging
LOG = logging.getLogger(__name__)

#found through testing that ~5-6 tasks at a time saturates the CPU
_MAX_TASKS = 5

def start(urls, output):
    '''
    Given an iterable of URLs and a target output directory
    attempt to Zotero the URLs and direct their output to the directory
    '''
    ret = []
    for batch in _get_batches(urls, batch_size=_MAX_TASKS):
        zh = _Zoteroing_Helper( batch, output, num_tasks=len(batch))
        
        res = _try_Zoteroing(zh)

        ret.extend( res )

    return ret

#source: https://docs.python.org/3/library/itertools.html#itertools-recipes
def _grouper(iterable, n, fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    from itertools import zip_longest
    return zip_longest(*args, fillvalue=fillvalue)

def _get_batches(urls, batch_size=_MAX_TASKS):
    batches = []
    
    #here we use grouper() to create sets of n items from the list
    #if there aren't enough elements to make a complete set of n
    #then None's are added to a group to make a set of n items
    for batch in _grouper(urls, batch_size, fillvalue=None):
        _batch = list(batch)
        #here we check for None's in each batch
        try:
            i = _batch.index(None)
        except ValueError:
            pass
        else:
            #and if there are None's in the list, then prune them off
            #making a batch that is smaller than n, but contains only
            #items from the list
            _batch = _batch[:i]

        #we then return a list of batches of items from the list that are at
        #most n long
        batches.append(_batch)

    return batches

def _try_Zoteroing(zh):
    while True:
        import lib.util as util
        if util.network_connected():
            LOG.debug("Starting Zoteroing")
            #start network montioring
            from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
            _nmh = NMH()
            _nmh.start()

            LOG.debug("network monitoring started")

            #start the search process with the search engine
            try:
                res = zh.start()
                LOG.debug("Zoteroing complete")
            except:
                #on an exception from the search engine, stop network monitoring
                #check for interruptions
                LOG.debug("saw an exception during Zotering")

                network_was_up = _nmh.stop()

                #if the network was up, then raise whatever
                #exception was thrown
                #otherwise, retry with the same configuration, and once the
                #network is back up
                if network_was_up:
                    LOG.debug("network was up during Zoteroing, so raising")
                    raise
                zh.stop()
            else:
                #then if the Zoteroing completed without exception
                #check for network issues again
                #if there were some during the Zoteroing
                #then retry the search when the network is up
                LOG.debug("checking for network issues in an otherwise successful search")
                network_was_up = _nmh.stop()
                zh.stop()
                if network_was_up:
                    LOG.debug("fully successful Zoteroing!")
                    return res

                LOG.debug("network problems during Zoteroing, retrying")
        else:
            LOG.debug("Network not connected, waiting...")

        import time
        time.sleep(1)

class _Zoteroing_Helper:
    def __init__(self, urls, output_dir, num_tasks=None):
        import lib.util as util
        if not util.is_iterable(urls):
            import lib.exceptions as exp
            raise exp.Bad_argument(f"Argument `urls` should be iterable of URLs.")
        
        for _u in urls:
            if not util.is_URL(_u):
                _m = f"Argument `urls` contained malformd item: {_u}."
                _m += "\n"
                _m = f"Note that only publicly accessibly URLs are considered valid."
                import lib.exceptions as exp
                raise exp.Bad_argument(_m)

        self._urls = [str(_) for _ in urls]

        if len(self._urls) == 0:
            import lib.exceptions as exp
            raise exp.Bad_argument(f"Argument `urls` should have at least one item.")
        
        if not num_tasks is None:
            import lib.util as util
            if not util.is_int(num_tasks):
                import lib.exceptions as exp
                raise exp.Bad_argument(f"Argument `num_tasks` should be integer.")

            if not (num_tasks >= 1):
                import lib.exceptions as exp
                raise exp.Bad_argument(f"Argument `num_tasks` should be >= 1.")

            self._max_tasks = int(num_tasks)
        else: #num_tasks is None
            self._max_tasks = min( [len(self._urls), _MAX_TASKS] )

        import lib.util as util
        if not util.is_valid_path(output_dir):
            import lib.exceptions as exp
            raise exp.Bad_argument(f"No such directory: {output_dir}")

        from pathlib import Path
        self._code_dir = str(Path("./lib/service_share/zotero_worker").absolute())
        self._output_dir = str(Path(output_dir).absolute())

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        self._output_helper = _zoteroing_output_helper(self._output_dir)

        self._image = "zotero_connector_and_standalone_worker"

        self._URL_to_container = {}
        self._service = None
    
    #---------------------------------------------------------------------------
    #Setup
    #---------------------------------------------------------------------------

    def _startup_Zoteroing_service(self, image_name, code_dir, output_dir, _replicas):
        LOG.debug("starting Zoteroing service")

        from lib.docker.service_helper import _Service_Helper as SH
        _sh = SH(image_name, replicas=_replicas)
        
        from pathlib import Path
        _src1 = str(Path(code_dir).resolve())
        _dst1 = "/home/headless/bin"

        from pathlib import Path
        _src2 = str(Path(output_dir).resolve())
        _dst2 = "/home/headless/tmp"

        _sh.mount(_src1, _dst1)
        _sh.mount(_src2, _dst2)

        _sh.start()

        return _sh

    #---------------------------------------------------------------------------
    #Main Loop
    #---------------------------------------------------------------------------

    def start(self):
        self._service = self._startup_Zoteroing_service(
            self._image, self._code_dir, self._output_dir, self._max_tasks
            )

        self._start(self._service, self._output_dir)

        #after finished with the Zoteroing, then return information about
        #each URL, the Zoteroing process for each, and if there were errors
        return self._compile_reports_of_finished_URLs(self._output_dir)

    def _start(self, service, output_dir):
        LOG.debug("Starting monitoring")
        while True:
            self._assign_URLs_to_tasks(service)

            self._prune_finished_tasks(output_dir)

            if self._all_done(service):
                self._stop()
                return

            LOG.debug("Continuing...")

            import time
            time.sleep(15)

    def stop(self): return self._stop()

    def _stop(self):
        if not self._service is None:
            if self._service.is_running():
                self._service.stop()
                del self._service
                self._service = None

    #---------------------------------------------------------------------------
    #Assigning URLs to tasks for work
    #---------------------------------------------------------------------------

    def _assign_URLs_to_tasks(self, service):
        '''
        process URLs in batches of self._max_tasks
            as there are never more than self._max_tasks of containers ready
        by finding the number of ready containers, and then assigning them URLs
        the number of containers and URLs should be equal, and should be the minimum
        of the two number
            e.g., if there are 2 URLs and three containers, then pass two of each
            to assign the remaining URLs to some of the idle containers
            if there are 4 URLs and 3 containers, when pass in three of each
            to start working on 3 URLs and use up the IDLE containers
            leaving 1 URL for the next pass
        '''
        LOG.debug("Assigning URLs to containers")
        _ready_containers = self._get_ready_containers(service)
        _num_new_jobs = min( len(self._urls), len(_ready_containers) )

        LOG.debug(f"Number of URLs left to process: {len(self._urls)}")
        LOG.debug(f"Number of ready containers to process them: {len(_ready_containers)}")

        _urls = []
        _containers = []
        for i in range(_num_new_jobs):
            if len(self._urls) == 0:
                break

            _urls.append( self._urls.pop() )
            _containers.append( _ready_containers[i] )

        for i in range(len(_urls)):
            _url = _urls[i]

            LOG.debug("Starting Zoteroing for URL:")
            LOG.debug(_url)

            _c = _containers[i]

            #start the Zoteroing process on a container for that URL
            _c.exec(f"python3 /home/headless/bin/run.py {_url}")

            #then also, startup screenshot monitoring to help detect faults
            _c.exec(f"python3 /home/headless/bin/screenshot_monitoring.py")

            #then make a record of what container the URL is associated with
            self._URL_to_container[_url] = _c

    def _get_ready_containers(self, service):
        '''
        return a list of containers that are IDLE, and are not assigned to a
        URL
        so that the containers can be assigned to work on URLs
        '''
        LOG.debug("Finding containers that are ready for Zoteroing.")
        _idle_containers = self._get_idle_containers(service)

        _assigned_container_ids = {_c.id():_c for _c in self._URL_to_container.values()}
        _idle_container_ids = {_c.id():_c for _c in _idle_containers}

        ids1 = set(list(_idle_container_ids.keys()))
        ids2 = set(list(_assigned_container_ids.keys()))
        _ready_ids = ids1 - ids2

        LOG.debug(f"Number of ready containers seen: {len(_ready_ids)}")

        return [_idle_container_ids[_id] for _id in _ready_ids]

    #---------------------------------------------------------------------------
    #Getting rid of tasks that are done
    #---------------------------------------------------------------------------

    def _prune_finished_tasks(self, output_dir):
        #monitoring the output directory for finished URLs
        _finished_URLs = self._output_helper.get_finished_URLs()

        if len(_finished_URLs) > 0:
            LOG.debug("Found some URLs that seem to be finished:")
            LOG.debug(_finished_URLs)

        #if we found a URL that seems to be finished, see if we have a container
        #associated with it
        #and if the container is idle, stop that container
        #and remove that URL from tracking
        for _url in _finished_URLs:
            if self._is_URL_done(_url):
                _container = self._URL_to_container[_url]
                _container.stop()
                del self._URL_to_container[_url]

    #---------------------------------------------------------------------------
    #Checks to see if all tasks are complete
    #---------------------------------------------------------------------------

    def _all_done(self, service):
        '''
        Check if we've consumed all the URLs and all the work is done with them
        '''
        _URLs_done = self._are_all_URLs_Zoteroed(
            self._urls, self._URL_to_container
            )
        _containers_done = self._are_all_containers_finished(service)
        if _URLs_done and _containers_done:
            return True
        return False

    def _are_all_URLs_Zoteroed(self, urls, URL_to_container):
        _urls_finished1 = (len(urls) == 0)
        _urls_finished2 = (len(list(URL_to_container.keys())) == 0)
        return (_urls_finished1 and _urls_finished2)

    def _are_all_containers_finished(self, service):
        _num_containers = len( service.containers() )
        _num_idle_containers = len(self._get_idle_containers(service))
        
        assert (_num_containers >= _num_idle_containers)

        return (_num_containers == _num_idle_containers)

    def _is_URL_done(self, url):
        if url in self._URL_to_container:
            LOG.debug("URL is associated with an active container:")
            LOG.debug(url)

            _container = self._URL_to_container[url]

            if self._is_container_idle( _container ):
                LOG.debug("container is finished processing:")
                LOG.debug(url)

                if self._output_helper.is_URL_done(url):
                    LOG.debug("URL has Zoteroing output")
                    LOG.debug(url)

                    return True
        return False        
    
    #---------------------------------------------------------------------------
    #Utilities
    #---------------------------------------------------------------------------

    def _get_idle_containers(self, service):
        _containers_idle = []
        _containers = service.containers()

        for _c in _containers:
            if self._is_container_idle( _c ):
                _containers_idle.append( _c )

        return _containers_idle

    def _is_container_idle(self, _container):
        _cmd = "python3 /home/headless/bin/status.py"
        _ret = _container.exec(_cmd, stdout=True, detach=False)
        _status = str(_ret.output.decode()).rstrip()
        return (_status == "IDLE")

    def _compile_reports_of_finished_URLs(self, output_dir):
        p2c = self._output_helper.paths_and_content()

        _reports = []
        for (path, content) in p2c.items():
            from pathlib import Path
            _path = Path(path)

            _res = {}
            _res["URL"] = content["URL"]
            _res["error"] = content["error"]
            _res["error msg"] = content["error msg"]
            _res["path"] = str(_path / "My Library")

            _reports.append( _res )

        return _reports