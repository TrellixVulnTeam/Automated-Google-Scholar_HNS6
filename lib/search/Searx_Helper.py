import lib.logging as logging
LOG = logging.getLogger(__name__)

def search(query, page=1, since=None, until=None):
    _sh = Searx_Helper(query, page, since, until)
    return _sh.run()

'''
BUG
there's some sort of issue with the Searx code that if the "since" and "until"
parameters are not defined (or are None) then no results are returned
this might be in the internal code to the Searx server
for now, defining the relevant parameters to sensible defaults, if not
passed in
'''
class Searx_Helper:
    def __init__(self, query, page=1, since=None, until=None):
        import lib.search._search_input_validator as SIV
        self._params = SIV.validate(query, page, since, until)

        self._image = "searx_server"

        self._service = None
        self._container = None

    #---------------------------------------------------------------------------
    #Setup
    #---------------------------------------------------------------------------

    def _startup_service(self, image_name, replicas):
        from lib.docker.service_helper import _Service_Helper as SH
        _sh = SH(image_name, replicas=replicas)
        _sh.environment("BASE_URL", "http://localhost:8080/")
        _sh.publish(8080, 8080)
        _sh.start()

        return _sh

    def _configure_searx(self, container):
        '''
        Modify an existing settings.yml
        and copy it to the searx server
        + reset and wait for it come up

        the searx server is already configured with:
        
        a custom google engine that allows for using advanced features
        of Goolge Scholar
            see: ./lib/service_share/searx_worker/google_scholar.py
        '''
        from pathlib import Path
        _config = Path("./lib/service_share/searx_worker/settings.yml")
        #load the template configuration
        with open(_config, 'rb') as f:
            import yaml
            config = yaml.safe_load( f )

        '''
        create a secret key
        as per searx recommendation and
        and flask recommended procedure
        see:
        https://github.com/searx/searx/issues/1473
        https://github.com/searx/searx/issues/834
        https://flask.palletsprojects.com/en/1.0.x/quickstart/#sessions
        '''
        import os
        config['server']['secret_key'] = str( os.urandom(16) )

        #then disable all search engines, except for Scholar
        for engine in config['engines']:
            #skip the engine we want to use
            if engine['name'] == "google scholar":
                engine['disabled'] = False
            else:
                #but otherwise, disable all the others
                engine['disabled'] = True

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdirname:
            from pathlib import Path
            _tmpdir = Path(tmpdirname)

            pth_tmp_file = _tmpdir / "settings.yml"
            pth_tmp_file.touch()

            import yaml
            pth_tmp_file.write_text( yaml.dump( config ) )

            #then remove the old configuration
            container.exec(f"rm -f /etc/searx/settings.yml")

            #and copy the new configuration file in
            container.cp_to( str(pth_tmp_file), '/etc/searx/' )

        container.restart()

        #then wait for the Searx server to come back up
        import lib.util as util
        util.wait_for( self._is_running )

    def _setup(self):
        self._service = self._startup_service(self._image, 1)

        self._container = self._service.containers()[0]

        self._configure_searx(self._container)

    #---------------------------------------------------------------------------
    #Main
    #---------------------------------------------------------------------------

    def run(self): 
        self._setup()

        res = self._search(self._params)

        self._stop()

        return res

    def _search(self, params):
        _searx_params = {
            'q': "",
            'format': "json",
            'engines': "google scholar",
            'pageno': 1, #which pages of results to return first
        }

        #BUG, setting "as_ylo" and "as_yhi" to sensible defaults
        from datetime import datetime
        current_year = datetime.now().year
        _query = {
            "query": "", #text of query
            "as_ylo": 1, #since
            "as_yhi": int(current_year), #until
        }

        _query["query"] = params['query']
        if "since" in params:
            _query["as_ylo"] = params["since"]
        if "until" in params:
            _query["as_yhi"] = params["until"]

        #here we set the `q` parameter to JSON, so that the patched Google Scholar
        #search engine code inside Searx can pick up on the extra options we pass
        #(since and until)
        import json
        _searx_params['q'] = json.dumps( _query )
        _searx_params['pageno'] = int(params['page'])

        import requests
        url = 'http://localhost:8080/search'
        res = requests.get(url, params=_searx_params).json()

        if not 'results' in res:
            return []

        return [result['url'] for result in res['results']]

    #---------------------------------------------------------------------------
    #Util
    #---------------------------------------------------------------------------

    def _stop(self):
        self._service.stop()
        self._service = None
        self._container = None

    def _is_running(self):
        if (self._service is None) or (self._container is None):
            return False

        #first, check that the docker container has a status of "running"
        _first = self._container.is_running()
        
        #then check that the linux environment is running
        _kwargs = {"stdout":True, "stderr":True, "detach":False}
        res = self._container.exec("cat /etc/searx/settings.yml", **_kwargs)
        _second = (res.exit_code == 0)

        #finally, check if the Searx server is running
        _third = False
        import requests
        try:
            if requests.get(f'http://localhost:8080/search').status_code == 200:
                _third = True
        except requests.exceptions.RequestException:
            pass

        return (_first and _second and _third)