import logging
LOG = logging.getLogger(__name__)

class _Timeout_Exception(Exception):
    '''
    A custom exception class to handle timeouts specifically
    see:
    https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
    '''
    pass

def _timeout_handler(signum, frame):
    LOG.debug(f"Timed out")
    raise _Timeout_Exception()

def wait_for(func, _timeout=None):
    return _wait_for(func, _timeout)

def _wait_for(func, _timeout=None):
    '''
    Wait for a function to return True
    see:
    https://stackoverflow.com/questions/492519/timeout-on-a-function-call
    '''
    LOG.debug(f"Waiting for function")

    import signal
    signal.signal(signal.SIGALRM, _timeout_handler)
    if _timeout is None:
        signal.alarm(60*1)
    else:
        signal.alarm(_timeout)

    try:
        while True:
            if func():
                LOG.debug(f"Function returned")
                signal.alarm(0) #reset the signal since the function returned
                return True

            import time
            time.sleep(1)
    except _Timeout_Exception:
        LOG.debug(f"Timed out waiting for function")
        return False

class Timer:
    def __init__(self, _time=60*1):
        import time
        self._start_time = time.time()
        self._timeout = _time

    def timed_out(self):
        import time
        return ((time.time() - self._start_time) >= self._timeout)

def is_process_live(name):
    return _is_process_live(name)

def _is_process_live(name):
    import psutil
    _processes = list()
    for proc in psutil.process_iter(['pid', 'name']):
        #LOG.debug(f"Checking: {proc.name()}")

        '''
        BUG
        at times a process may disappear betwen then psutil puts it in the
        iterator, and when it's checked here
        so, if the process isn't present, then skip this process
        '''
        import psutil
        try:
            _found_name = (str(name).lower() in str(proc.name()).lower())
            _found_live = (str(proc.status()) != 'zombie')
        except psutil.NoSuchProcess:
            continue

        if (_found_name):
            LOG.debug(f"Found the process: {name}")

            if (_found_live):
                LOG.debug(f"Process is alive: {name}")

        if (_found_name and _found_live):
            LOG.debug(f"Found a live process: {name}")
            return True

    LOG.debug(f"Could not find live process: {name}")
    return False

def waiting_for_process(name):
    return _waiting_for_process(name)

def _waiting_for_process(name):
    def _stub():
        return _is_process_live(name)

    return _wait_for( _stub )

def _SIGINT_proc(p):
    LOG.debug(f"SIGINT process: {p}")
    import signal
    p.send_signal(signal.SIGINT)

def _SIGHUP_proc(p):
    LOG.debug(f"SIGHUP process: {p}")
    import signal
    p.send_signal(signal.SIGHUP)

def _term_proc(p):
    LOG.debug(f"Terminate process: {p}")
    p.terminate()

def _kill_proc(p):
    LOG.debug(f"Kill process: {p}")
    p.kill()

def close_process(name):
    return _close_process(name)

def _close_process(name):
    LOG.debug(f"Closing {name}.")
    
    if not _is_process_live(name):
        LOG.debug(f"{name} wasn't running to close")
        return False

    _proc = None
    import psutil
    for proc in psutil.process_iter(['pid', 'name']):
        _found_name = (str(name).lower() in str(proc.name()).lower())
        _found_live = (str(proc.status()) != 'zombie')

        if (_found_name and _found_live):
            LOG.debug(f"Found process: {name}")
            _proc = proc

    def _stub():
        return (not _is_process_live(name))

    #try to close the processes in progressively more extreme ways
    #waiting a few moments between attempts
    for _k in [_SIGINT_proc, _SIGHUP_proc, _term_proc, _kill_proc]:
        _k(_proc)

        #waiting for process to close
        if _wait_for( _stub, _timeout=2 ):
            LOG.debug(f"Closed: {name}")
            return True

    LOG.debug(f"Couldn't close: {name}")
    return False

def get_clipboard():
    '''
    return the text that's on the clipboard
        see: https://ostechnix.com/access-clipboard-contents-using-xclip-and-xsel-in-linux/
    '''
    import subprocess
    res = subprocess.run(['xclip', '-o', '-sel', 'clip'], capture_output=True)
    return res.stdout.decode()

def is_URL(_url):
    '''
    Check if a string is a valid URL
        see:
        https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
        https://docs.python.org/3/library/urllib.parse.html
    '''

    if not isinstance(_url, str):
        return False

    from urllib.parse import urlparse

    try:
        result = urlparse(_url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False