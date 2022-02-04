'''
Motivation

During the scraping process we want to track what page we're on, as well as
what URL we're working with; In-case of interruption
This class creates a "resume file" (resume.tar) at its path that can track
that information
The scraper than just has to call helper functions on this object
    e.g., page_begin, page_end, etc
to record different steps of the scraping process in the resume file
Then, if we need to resume a scraping process after an interruption
This object will automatically load the resume file, set its state, and can
be used to query where to resume the scraping process

Also it has a helper function (get_URLs) that can be used to query the resume
file for which URLs have been seen and logged before
So we can determine which URLs on a page have and have not been completed
before; Just be finding the difference between what's observed, and the URLs
from the log.
'''
import lib.logging as logging
LOG = logging.getLogger(__name__)

class _scraping_tracker:
    def __init__(self, pth):
        import lib.util as util
        if not util.is_valid_path(pth):
            import lib.exceptions as exp
            raise exp.Bad_argument(f"Bad path: {pth}")

        from pathlib import Path
        self._output_path = Path(pth)

        self._resume_file_name = "resume.tar"

        setup_results = self._setup(self._output_path, self._resume_file_name)

        self._resume_file = setup_results["resume_file"]
        self._current_page = setup_results["current_page"]
        self._current_URL = setup_results["current_URL"]
        self._current_log_id = setup_results["current_log_id"]

    def _setup(self, resume_file_path, resume_file_name):
        from pathlib import Path
        path = Path(resume_file_path)

        resume_file = path / str(resume_file_name)

        res = {}
        res["resume_file"] = str(resume_file.resolve())
        res["current_page"] = 1
        res["current_URL"] = None
        res["current_log_id"] = 0

        if not resume_file.exists():
            resume_file.touch()

            #make an empty tar archive
            #see: https://bugs.python.org/issue6123
            #https://superuser.com/questions/448623/how-to-get-an-empty-tar-archive
            #https://docs.python.org/3/library/tarfile.html#tarfile.TarInfo
            import tarfile
            content = tarfile.TarInfo()
            tar = tarfile.open(resume_file, mode="w", tarinfo=content)
            tar.close()            
        else:
            loaded = self._load(resume_file)
            if "current_page" in loaded:
                res["current_page"] = int(loaded["current_page"])

            if "current_URL" in loaded:
                res["current_URL"] = str(loaded["current_URL"])

            if "current_log_id" in loaded:
                res["current_log_id"] = int(loaded["current_log_id"])

        return res

    def _load(self, resume_file):
        '''
        Given an existing resume file, load state from it    
        message format
        {
        'current page': '1',
        'current URL': 'None',
        'log': 'begin page: 1',
        '_timestamp': '2021-12-23T18:06:30.545849',
        '_file_name': 'C:\\Users\\pmatt\\AppData\\Local\\Temp\\tmp7t7i5g2u\\0.json'
        }   
        '''
        latest = None
        _id = None
        res = {}

        for log in self._get_logs(resume_file):
            from pathlib import Path
            file_name = Path(log["_file_name"])
            if latest is None:
                latest = log
                _id = file_name.stem

            from datetime import datetime
            latest_time = datetime.fromisoformat(latest["_timestamp"])
            loaded_time = datetime.fromisoformat(log["_timestamp"])

            if loaded_time > latest_time:
                latest = log
                _id = file_name.stem

        if not latest is None:
            res["current_page"] = int( latest['current page'] )
            res["current_URL"] = latest['current URL']
            res["current_log_id"] = int(_id)

        return res

    def _get_logs(self, resume_file_path):
        '''
        message format
        {
        'current page': '1',
        'current URL': 'None',
        'log': 'begin page: 1',
        '_timestamp': '2021-12-23T18:06:30.545849',
        '_file_name': 'C:\\Users\\pmatt\\AppData\\Local\\Temp\\tmp7t7i5g2u\\0.json'
        }
        '''
        res = []

        from pathlib import Path
        resume_file = Path(resume_file_path)
        if not resume_file.exists():
            return []

        #make a temporary directory to extract the contents of the resume file
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            from pathlib import Path
            pth = Path(td)

            #extract the contents of the resume file
            import tarfile
            try:
                with tarfile.open(resume_file, 'r') as tar:
                    tar.extractall(path=pth)
            except tarfile.ReadError:
                return []

            for f in pth.iterdir():
                import json
                loaded = json.loads( f.read_text() )
                loaded["_file_name"] = str(f)
                
                res.append( loaded )

        return res

    def page(self, set=None):
        if not set is None:
            import lib.util as util
            if not util.is_int(set):
                import lib.exceptions as exp
                raise exp.Bad_argument("Argument `set` should be integer.")
            self._current_page = int(set)

        return self._current_page

    def url(self, set=None):
        if not set is None:
            import lib.util as util
            if not util.is_URL(set):
                import lib.exceptions as exp
                msg = f"Argument `set` doesn't look like a public URL: {set}."
                raise exp.Bad_argument(msg)

            self._current_URL = str(set)

        return self._current_URL

    def page_begin(self):
        msg = {}
        msg["current page"] = str(self._current_page)
        msg["current URL"] = str(self._current_URL)
        msg["log"] = f"begin page: {self._current_page}"

        return self._append( msg,  self._resume_file)

    def page_end(self):
        msg = {}
        msg["current page"] = str(self._current_page)
        msg["current URL"] = str(self._current_URL)
        msg["log"] = f"end page: {self._current_page}"

        return self._append( msg,  self._resume_file)

    def url_begin(self):
        msg = {}
        msg["current page"] = str(self._current_page)
        msg["current URL"] = str(self._current_URL)
        msg["log"] = f"begin URL: {str(self._current_URL)}"

        return self._append( msg,  self._resume_file)

    def url_end(self):
        msg = {}
        msg["current page"] = str(self._current_page)
        msg["current URL"] = str(self._current_URL)
        msg["log"] = f"end URL: {str(self._current_URL)}"

        return self._append( msg,  self._resume_file)

    def _json_serial(self, obj):
        """
        JSON serializer for objects not serializable by default json code
            see:
            https://stackoverflow.com/a/22238613/5343977
        """

        from datetime import date, datetime
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))

    def _append(self, msg, resume_file):
        '''
        msg; a dict containing information to writeout to the resume_file
        '''
        _msg = msg.copy()
        _raw = None
        import tarfile
        with tarfile.open(resume_file, 'a') as tar: #appending to the archive
            #write out a temporary file that we can put information into
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                from pathlib import Path
                pth = Path(td)

                import datetime
                _msg["_timestamp"] = datetime.datetime.now()

                #name the temporary file to the heartbeat
                tmp_file = pth / f"{self._current_log_id}.json"
                tmp_file.touch()
                import json
                _raw = json.dumps(_msg, default=self._json_serial)
                tmp_file.write_text( _raw )

                tar.add( tmp_file, arcname=tmp_file.name )

        self._current_log_id += 1

        from pathlib import Path
        return {
            "resume_file": str( Path( resume_file ).resolve() ),
            "message": _msg,
            "_raw": str(_raw)
        }

    def get_URLs(self): return self._get_URLs(self._resume_file)

    def _get_URLs(self, resume_file):
        res = []
        for log in self._get_logs(resume_file):
            '''
            format
            {
            'current page': '1',
            'current URL': 'None',
            'log': 'begin page: 1',
            '_timestamp': '2021-12-23T18:06:30.545849',
            '_file_name': 'C:\\Users\\pmatt\\AppData\\Local\\Temp\\tmp7t7i5g2u\\0.json'
            }
            '''
            if 'current URL' in log:
                if ((not log['current URL'] is None) and 
                    (log['current URL'] != 'None')):
                    res.append( str( log['current URL'] ) )

        #then return only the unique URLs seen
        return list(set(res))