import lib.logging as logging
LOG = logging.getLogger(__name__)

'''
A regex that identifies URLs
    see:
    https://gist.github.com/dperini/729294#file-regex-weburl-js-L88
    https://mathiasbynens.be/demo/url-regex
'''
import re
_URL_identification_regex = re.compile(
    "^" +
        #protocol identifier (optional)
        #short syntax // still required
        "(?:(?:(?:https?|ftp):)?\\/\\/)" +
        #user:pass BasicAuth (optional)
        "(?:\\S+(?::\\S*)?@)?" +
        "(?:" +
            #IP address exclusion
            #private & local networks
            "(?!(?:10|127)(?:\\.\\d{1,3}){3})" +
            "(?!(?:169\\.254|192\\.168)(?:\\.\\d{1,3}){2})" +
            "(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})" +
            #IP address dotted notation octets
            #excludes loopback network 0.0.0.0
            #excludes reserved space >= 224.0.0.0
            #excludes network & broadcast addresses
            #(first & last IP address of each class)
            "(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])" +
            "(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}" +
            "(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))" +
        "|" +
            #host & domain names, may end with dot
            #can be replaced by a shortest alternative
            #(?![-_])(?:[-\\w\\u00a1-\\uffff]{0,63}[^-_]\\.)+
            "(?:" +
                "(?:" +
                    "[a-z0-9\\u00a1-\\uffff]" +
                    "[a-z0-9\\u00a1-\\uffff_-]{0,62}" +
                ")?" +
                "[a-z0-9\\u00a1-\\uffff]\\." +
            ")+" +
            #TLD identifier name, may end with dot
            "(?:[a-z\\u00a1-\\uffff]{2,}\\.?)" +
        ")" +
        #port number (optional)
        "(?::\\d{2,5})?" +
        #resource path (optional)
        "(?:[/?#]\\S*)?" +
    "$", flags=re.IGNORECASE
)#end

def wait_for(func, _timeout=None): return _wait_for(func, _timeout)

def _wait_for(func, _timeout=None):
    '''
    Wait for a function to return True
    see:
    https://stackoverflow.com/questions/492519/timeout-on-a-function-call
    '''
    LOG.debug(f"Waiting for function")

    import time
    start_time = time.time()
    timeout = None
    if _timeout is None:
        timeout = 60*1
    else:
        timeout = _timeout

    while True:
        if func():
            LOG.debug(f"Function returned")
            return True

        if abs(time.time() - start_time) >= timeout:
            LOG.debug(f"Timed out waiting for function")
            return False

        import time
        time.sleep(1)

def get_short_path_name(_path):
    '''
    Given a windows path, return a shortened 8.3 version of the path
    and in posix
    useful for windows filenames with difficult characters in them
        e.g., spaces, commas, etc.
    '''

    from pathlib import Path
    path = Path(_path).absolute()

    #source: https://stackoverflow.com/a/10227715/5343977
    import subprocess
    _cmd = f'cmd /c for %A in ("{str(path)}") do @echo %~sA'
    _ret = subprocess.run(_cmd, capture_output=True)

    if _ret.returncode == 0:
        return str(Path( _ret.stdout.decode() ).as_posix()).rstrip()

    return None

#-------------------------------------------------------------------------------
#Argument checks
#-------------------------------------------------------------------------------

def is_iterable(obj): return _is_iterable(obj)

def _is_iterable(obj):
    if isinstance(obj, str): return False
    
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def is_valid_path(_path): return _is_valid_path(_path)

def _is_valid_path(_path):
    if not _is_pathlike(_path):
        return False

    from pathlib import Path
    if not Path(str(_path)).exists():
        return False

    return True

def is_int(arg): return _is_int(arg)

def _is_int(arg):
    try:
        _i = int(arg)
    except ValueError:
        return False

    #check for the case of a float, since int() will trunacte floats
    if _i == float(arg):
        return True
    return False

def is_valid_page_number(num):
    if not _is_int(num):
        return False

    if not (1 <= num <= 50):
        return False

    return True

def is_valid_year(yr): return _is_valid_year(yr)

def _is_valid_year(yr):
    if not _is_int(yr):
        return False

    from datetime import datetime
    current_year = datetime.now().year

    if not (0 < yr <= current_year):
        return False

    return True

def are_valid_search_years(since, until):
    for yr in [since, until]:
        if not _is_valid_year(yr):
            return False

    if not (since <= until):
        return False

    return True

def is_pathlike(obj): return _is_pathlike(obj)

def _is_pathlike(obj):
    if len(str(obj)) == 0:
        return False

    if isinstance(obj, str):
        return True

    if isinstance(obj, bytes):
        return True

    import os
    if isinstance(obj, os.PathLike):
        return True

    from pathlib import PurePath
    if isinstance(obj, PurePath):
        return True

    #otherwise, duck-type it
    obj_attrbiutes = set(list(dir(obj)))

    #the __fspath__ attribute is required
    #as per: https://docs.python.org/3/library/os.html#os.PathLike
    from pathlib import PurePath
    if not ("__fspath__" in obj_attrbiutes):
        return False
    
    #and make sure it's a function
    fspath_type = type(getattr(PurePath, "__fspath__"))
    obj_fspath_type = type(getattr(obj, "__fspath__"))
    if not (fspath_type == obj_fspath_type):
        return False

    return True

#-------------------------------------------------------------------------------
#Networking
#-------------------------------------------------------------------------------

def is_valid_URL(url): return _is_valid_URL(url)

def _is_valid_URL(url):
    if not _network_connected():
        LOG.debug("Not connected to the Internet.")
        import lib.exceptions as exp
        raise exp.Not_connected("No internet connection")

    if not _is_URL(url): return False
    if not _is_URL_up(url): return False
    return True

def is_URL(_url): return _is_URL(_url)

def _is_URL(url):
    '''
    Check if a string is a URL

    ----

    NOTE

    This is a very difficult problem
    Several approaches were tested
        including failed approaches:
        
        from urllib.request import urlopen, URLError
        from http.client import InvalidURL
        urlopen(url)

        ----

        from urllib.parse import urlparse

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
        
        ----

        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError

        validate = URLValidator()

        try:
            validate(_url)
            return True
        except ValidationError:
            return False

    during testing the regex from:
        https://gist.github.com/dperini/729294#file-regex-weburl-js-L88
    and the library of more general validators, whose URL validator
    is also based off of that regex
        see:
        https://validators.readthedocs.io/en/latest/#module-validators.url
    proved to have very similar, but non-identical success rates
    thus the test because the OR of these two tests, which yields a very
    high success rate
    The URLs used for testing were lifted from these resources, as well
    as other examples URLs found during research

    ----

    resources used during research:
        see:
        https://cran.r-project.org/web/packages/rex/vignettes/url_parsing.html
        https://mathiasbynens.be/demo/url-regex
        https://stackoverflow.com/questions/5717093/check-if-a-javascript-string-is-a-url
        https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
        https://stackoverflow.com/questions/3170231/how-can-i-check-if-a-url-exists-with-django-s-validators
        https://stackoverflow.com/questions/22238090/validating-urls-in-python
        https://stackoverflow.com/questions/16778435/python-check-if-website-exists
    '''
    '''
    URL check 1, with the regx URL validator from:
    https://gist.github.com/dperini/729294#file-regex-weburl-js-L88
    https://mathiasbynens.be/demo/url-regex
    '''
    _res1 = False
    LOG.debug("Checking URL with `URL regex validator`")
    LOG.debug(url)
    import lib.util as util
    if (not util._URL_identification_regex.fullmatch(url) is None):
        _res1 = True

    '''
    URL check 2, with library "validators" from:
    https://validators.readthedocs.io/en/latest/#module-validators.url

    --

    Note that we use public=True here to only return True for URLs that contain
    IP addresses that are public
    This choice was made because of the implimentation of this software is
    only concerned with URLs that can be accessed over the public internet
    '''
    _res2 = False
    LOG.debug("Checking URL with `lib validators`")
    LOG.debug(url)
    import validators
    if validators.url(url, public=True) == True:
        _res2 = True

    return (_res1 or _res2)

def is_URL_up(url): return _is_URL_up(url)

def _is_URL_up(url):
    #first, check if we're connected
    if not _network_connected():
        LOG.debug("Not connected to the Internet.")
        import lib.exceptions as exp
        raise exp.Not_connected("No internet connection")

    #use request to try get a response from the URL
    #see:https://stackoverflow.com/questions/65572244/socket-gaierror-errno-11001-getaddrinfo-failed-in-python-while-using-a-simp
    #https://docs.python.org/3/library/urllib.request.html#module-urllib.request
    #https://docs.python.org/3/library/urllib.error.html
    from urllib import request
    from urllib import error
    import socket
    try:
        res = request.urlopen(url)
        LOG.debug(f"Opened the URL without issue: {url}")
    except error.HTTPError:
        #no issues with the URL itself
        #so it's reachable enough to do HTTP
        #which is what we want
        LOG.debug(f"Saw an HTTP error, but the URL seems okay: {url}")
        return True
    except error.URLError:
        LOG.debug(f"Saw an issue with the URL itself: {url}")
        #there's an issue with the URL
        return False
    except socket.timeout:
        LOG.debug(f"Timed out trying to open the URL: {url}")
        #there's an issue with the URL
        return False

    return True

def network_connected(): return _network_connected()

def _network_connected():
    '''
    Try three progressively
    more complex (and slower)
    checks to see if we
    can reach google DNS
    if we can't, then the
    Internet is likely down
    '''
    _google_DNS = ["8.8.8.8", "8.8.4.4"]

    for _ip in _google_DNS:
        if _DNS_socket_connect(_ip):
            return True

        if _netcat_DNS(_ip):
            return True

        if _nmap(_ip)['up']:
            return True

    return False

#-------------------------------------------------------------------------------
#Low level Networking
#-------------------------------------------------------------------------------

def _DNS_socket_connect(ip):
    port=53
    timeout=3
    
    import contextlib
    import io
    import socket
    f = io.StringIO()
    with contextlib.redirect_stderr(f), contextlib.redirect_stdout(f):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip, port))
            return True
        except socket.error as ex:
            LOG.debug(ex)
    return False

def _netcat_DNS(ip):
    str_args = f'nc {ip} 53 -zv'

    import subprocess
    res = subprocess.run(str_args, capture_output=True, shell=True)

    if "open" in res.stderr.decode():
        return True
    return False

def _nmap(ip):
    '''
    A thorough, but slow, check
    to see if an IP is up

    return their state (up or down)
    and any open ports
    see:
    https://stackoverflow.com/questions/3764291/checking-network-connection
    '''
    LOG.debug(f"nmap()ing ip: {ip}")

    d_ret = {'up' : False, 'open_port': []}

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        from pathlib import Path
        xml_output = Path(tmpdir).resolve() / "nmap_output.xml"
        
        #do a default nmap SYN scan on target
        #and store the output as XML in nmap_output.xml
        #since nmap doesn't do JSON
        str_args = f'nmap -sS -oX {xml_output} {ip}'

        import subprocess
        res = subprocess.run(str_args, capture_output=True, shell=True)

        if res.returncode != 0:
            LOG.debug("nmap execution error, giving up")
            return d_ret

        #then parsing the XML into something we can use
        #see: https://avleonov.com/2018/03/11/converting-nmap-xml-scan-reports-to-json/
        import xmltodict
        import xml
        try:
            d_response = xmltodict.parse( xml_output.read_text() )
        except xml.parsers.expat.ExpatError:
            LOG.debug("Error parsing nmap output, giving up")
            LOG.debug("xml.parsers.expat.ExpatError")
            return d_ret
        except xmltodict.ParsingInterrupted:
            #see: https://github.com/martinblech/xmltodict/blob/master/tests/test_xmltodict.py
            LOG.debug("Error parsing nmap output, giving up")
            LOG.debug("ParsingInterrupted")
            return d_ret

        #checking the structure of the parsed info
        if not "nmaprun" in d_response:
            return d_ret

        #no internet connection case
        if not "host" in d_response["nmaprun"]:
            return d_ret

        if not ( ("status" in d_response["nmaprun"]["host"]) and
        ("@state" in d_response["nmaprun"]["host"]["status"]) ):
            return d_ret

        #get the state of the target (up or down)
        if "up" in str(d_response["nmaprun"]["host"]["status"]["@state"]):
            d_ret['up'] = True

        #and return any open ports
        if ("ports" in d_response["nmaprun"]["host"] and
        "port" in d_response["nmaprun"]["host"]["ports"]):
            for p in d_response["nmaprun"]["host"]["ports"]["port"]:
                if ("state" in p and ("@state" in p["state"]) ):
                    if "open" in p["state"]["@state"]:
                        if "@portid" in p:
                            d_ret['open_port'].append( int(p["@portid"]) )

    return d_ret