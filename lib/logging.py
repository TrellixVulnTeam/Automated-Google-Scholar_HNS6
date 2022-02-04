'''
A module to handle log setup, configuration, and address some of the more
annoying aspects of logging in a python environment
'''

'''
TODO

setup logging for individual modules, as well as large single log that shows
everything
'''

def _setup_logging():
    #do we have a log directory?
    from pathlib import Path
    log_dir = Path("./log")

    if not log_dir.exists():
        log_dir.mkdir()

    #and setup the log file to open with utf-8 encoding
    import logging
    import time
    _log_name = "main_" + str(time.time())
    str_path_log_file = str(log_dir / (_log_name + '.log'))
    kwds = {'filename': str_path_log_file,'mode':'a', 'encoding':'utf-8'}

    file_handler = logging.FileHandler( **kwds )

    #then for the console logger, set it up to show only DEBUG statements
    import sys
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    #setup the root logger
    #see:
    #https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        #setup formatting for each log record
        #see: https://docs.python.org/3/library/logging.html#logrecord-attributes
        format="%(asctime)s; %(levelname)s [%(name)s:%(funcName)s] %(message)s",
        handlers=[
            file_handler,
            console_handler,
        ]
    )

def getLogger(_name):
    import logging
    return logging.getLogger(_name)

_init_setup = False

if not _init_setup:
    _setup_logging()

    #BUGFIX
    '''
    numexpr is a module loaded somewhere in the dependencies of networking_helper
    it does something to the root logger and then outputs logging info like:
        2021-12-03 00:30:14,675; INFO [numexpr.utils:_init_num_threads] NumExpr defaulting to 8 threads.
    with no way to disable after, so we disable it here before anything is loaded
    see:
    https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
    '''
    import logging
    logging.getLogger('numexpr').setLevel(logging.CRITICAL)

    #BUGFIX
    '''
    matplotlib has a similar issues and is disable similarly
    '''
    import logging
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)

    import logging
    logging.getLogger('docker').setLevel(logging.CRITICAL)

    import logging
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

    import logging
    logging.getLogger('bibtexparser').setLevel(logging.CRITICAL)

    _init_setup = True