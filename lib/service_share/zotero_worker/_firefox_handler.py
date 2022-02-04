'''
NOTE
if we ever need to worry about checking for if Firefox has focus
the easiest way seems to be to:
cycle through open windows with alt-tab
and
use the screenshot functionality to check if the window that has focus after
and alt-tab is firefox or not
'''
import logging
LOG = logging.getLogger(__name__)

_proc_name = 'firefox'
_page_loaded_screenshot = "/home/headless/bin/reference_done_loading.png"
_log_dir = "/home/headless/tmp/"
_log_prefix = "firefox_log"
_page_load_timeout = 60*2 #2 minutes

_first_ezproxy_login_attempt = False
_second_ezproxy_login_attempt = False
_ezproxy_logged_in = False

def start(_home="https://ezproxy.lib.ucalgary.ca/"): return _start(_home)

def _start(_home="https://ezproxy.lib.ucalgary.ca/"):
    LOG.debug("Starting Firefox")

    #first close any open firefox
    _close()

    LOG.debug("Setting up logging")

    #setup to enable firefox logging
    from pathlib import Path
    pth_firefox_logdir = Path( _log_dir )
    import os
    os.environ['MOZ_LOG'] = 'timestamp,rotate:200,nsHttp:5,cache2:5,nsSocketTransport:5,nsHostResolver:5,cookie:5'
    os.environ['MOZ_LOG_FILE'] = f'{str(pth_firefox_logdir)}/{_log_prefix}'

    #then open firefox to the Ucalgary proxy home page
    LOG.debug("Trying to start process")
    import subprocess
    subprocess.Popen(["firefox", _home])

    #then waiting for the firefox process to open
    import _util as util
    if not util.waiting_for_process(_proc_name):
        return False #something went wrong with opening Firefox

    #then waiting for the UI to appear and be usable
    LOG.debug("Waiting for UI to appear")
    return _is_UI_up()

class Cannot_close_Firefox(Exception): pass

def close():
    return _close()

def _close():
    LOG.debug("Closing Firefox.")

    if _is_running():
        _ret = []
        import _util as util
        _ret.append( util.close_process( _proc_name ) )
        _ret.append( _logs_cleanup() )

        if not any(_ret):
            raise Cannot_close_Firefox()

def is_running():
    return _is_running()

def _is_running():
    LOG.debug("Checking if Firefox is running")

    import _util as util
    return util.is_process_live(_proc_name)

def is_UI_up():
    return _is_UI_up()

def _is_UI_up():
    return (_is_running() and _is_page_loaded())

def is_page_loaded():
    return _is_page_loaded()

def _is_page_loaded():
    '''
    Check several different measures to see if we can guess if Firefox has
    loaded a page completely

    assume the page is loaded if:
    if we see only small changes in log file size over ~2 sample
    or
    log files are not being accessed over ~3 samples
    or
    if we see only small changes in log file size in at least 1 sample
    and
    log files are not being accessed over at least 2 samples
    and
    the screenshot seems to show a loaded page
    '''
    LOG.debug("Checking for Firefox running")
    if not _is_running():
        LOG.debug("Firefox is not running")
        return False

    LOG.debug("Firefox is running")

    LOG.debug("Finding logs")
    #wait for the firefox to be present
    import _util as util
    if not util.wait_for( _logs_present ):
        LOG.debug("Couldn't find Firefox logs")
        return False

    LOG.debug("Found logs")

    d_conditions = {}
    d_conditions['small changes to log file sizes'] = []
    _n_last_size = 0
    _l_log_file_changes = []

    d_conditions['logs not accessed'] = []
    _l_log_access_times = []

    d_conditions['screenshot positive'] = []

    import _util as util
    _timer = util.Timer( _page_load_timeout )

    while True:
        #first, check for changes in the size of the log files
        #is the latest change small, as compared with the running average?
        _latest_log_size = _log_file_size()
        _current_change = abs( _n_last_size - _latest_log_size )
        _l_log_file_changes.append(_current_change)
        import statistics as s
        _avg = s.mean(_l_log_file_changes)

        p = .10
        if _current_change <= (_avg*p):
            LOG.debug(f"Found a small change in the size of the log files: {_current_change}")
            d_conditions['small changes to log file sizes'].append(True)
        else:
            d_conditions['small changes to log file sizes'].append(False)

        LOG.debug(f"Changes seen: {_l_log_file_changes}")
        LOG.debug(f"Record of small changes seen: {d_conditions['small changes to log file sizes']}")

        _n_last_size = _latest_log_size

        if len(d_conditions['small changes to log file sizes']) >= 2:
            _rec = d_conditions['small changes to log file sizes']

            #check the last two entries, have we seen small changes in both?
            #if so, then return
            if all(_rec[-2:]):
                LOG.debug(f"Found at least two instances in a row of small log file changes")
                return True

        #second, check for log access times
        #have the logs not been accessed (written to) since last iteration?
        _l_log_access_times.append( _logs_change_times() )

        if len(_l_log_access_times) >= 2:
            _this_time = _l_log_access_times[-1]
            _last_time = _l_log_access_times[-2]

            '''
            Here we can deep-compare dicts, making sure they have the same
            keys, and those keys have the same values
            all with a ==
                see:
                https://stackoverflow.com/questions/1911273/is-there-a-better-way-to-compare-dictionary-values
            '''
            if _this_time == _last_time:
                LOG.debug(f"Found instance of logs not being accessed")
                d_conditions['logs not accessed'].append(True)
        d_conditions['logs not accessed'].append(False)

        #check the last three entries, have the logs not been accessed over
        #the last three samples?
        #if so, then return
        if len(d_conditions['logs not accessed']) >= 3:
            if all(d_conditions['logs not accessed'][-3:]):
                LOG.debug(f"Found at least three samples in a row of logs not being access")
                return True

        LOG.debug(f"Record of log access checks:")
        LOG.debug(d_conditions['logs not accessed'])

        #third, do a screenshot check to see if Firefox appears to be finished
        #loading
        #Does the firefox "loading" widget appear to be absent?
        d_conditions['screenshot positive'].append( _screenshot_loaded_check() )

        #finally, check for combinations of indicators that the page has loaded
        #do we have at least 1 instance of small changes in log files
        #and
        #two instances of log access times being stable?
        #and
        #do we have evidence from the screenshot check?
        _l_small_changes = d_conditions['small changes to log file sizes']
        _enough_small_changes = (len(_l_small_changes) >= 1)
        _enough_access_times = (len(d_conditions['logs not accessed']) >= 2)
        _enough_screenshots = (len(d_conditions['screenshot positive']) >= 1)
        if _enough_small_changes and _enough_access_times and _enough_screenshots:
            LOG.debug(f"Checking combinations of indicators that Firefox is loaded")
            _last_small_change = [_l_small_changes[-1]]
            _last_access_time_report = d_conditions['logs not accessed'][-2:]
            _last_screenshot_check = [d_conditions['screenshot positive'][-1]]

            LOG.debug(f"small changes")
            LOG.debug(_last_small_change)
            LOG.debug(f"access times")
            LOG.debug(_last_access_time_report)
            LOG.debug(f"screenshot check")
            LOG.debug(_last_screenshot_check)

            _check = []
            _check.extend(_last_small_change)
            _check.extend(_last_access_time_report)
            _check.extend(_last_screenshot_check)

            if all(_check):
                return True

        #otherwise timeout after a few minutes
        if _timer.timed_out():
            return False

        import time
        time.sleep(1)

def _get_log_files():
    '''
    return a list of Path objects for each firefox log file present
    '''

    from pathlib import Path
    pth_log = Path( _log_dir )

    _ret = []

    for itm in pth_log.glob(f"{_log_prefix}*"):
        #BUG, we can sometimes list a log file being present
        #which will then be removed, as Firefox rotates its
        #logs
        if not itm.exists(): continue

        _ret.append( itm.resolve() )

    return _ret

def _logs_present():
    '''
    Check if the Firefox logs are present or not
    '''
    LOG.debug("Checking for Firefox logs")
    import os
    from pathlib import Path
    pth_log = Path( _log_dir )

    return (len([frfx_log for frfx_log in pth_log.glob(f"{_log_prefix}*")]) > 0)

def _log_file_size():
    '''
    Get the cumulative size of the log files
    we use this to check if the size of the logs has changed significantly
    or not
    '''

    if not _logs_present():
        return 0

    LOG.debug("Checking size of Firefox logs")

    _ret = []

    for itm in _get_log_files():
        import os
        _ret.append( os.stat(itm).st_size )
    
    return sum(_ret)

def _logs_change_times():
    '''
    Query all of the Firefox log files for the last time they were changed
    returning a dict mapping log files names to when they were last changed
    '''

    LOG.debug("Checking for last changed time in Firefox logs")
    d_itms = {}

    if _logs_present():
        for itm in _get_log_files():
            import os
            res = os.stat(itm).st_mtime
            if str(itm.name) not in d_itms:
                d_itms[str(itm.name)] = res

    return d_itms

def is_running_with_loaded_page(): return _is_running_with_loaded_page()

def _is_running_with_loaded_page():
    return _is_UI_up()

class Trying_to_cleanup_logs_with_Firefox_running(Exception): pass

def logs_cleanup(): return _logs_cleanup()

def _logs_cleanup():
    '''
    Delete all the logs, as long as Firefox isn't running
    '''

    if not _logs_present():
        return True

    if _is_running():
        raise _Trying_to_cleanup_logs_with_Firefox_running()

    for itm in _get_log_files():
        itm.unlink()

    if not _logs_present():
        return True
    return False #some sort of issue prevented removing all of the logs

def _screenshot_loaded_check():
    '''
    Try to visually guage is the "loading icon" is present in Firefox or not
    We use this to try to check if a page is loaded in Firefox
    (not very reliable, but useful combined with other measures)
    '''
    LOG.debug("Screenshot check, if Firefox is loading a page")

    if _is_running():
        from PIL import Image
        import imagehash
        reference_image_hash = imagehash.phash(Image.open(_page_loaded_screenshot))

        from PIL import ImageGrab
        bbox = (0, 96, 136, 132)

        import imagehash
        latest_image_hash = imagehash.phash( ImageGrab.grab(bbox) )

        diff = abs(reference_image_hash - latest_image_hash)
        LOG.debug(f"Difference between reference image and current image: {diff}")

        if diff <= 12:
            return True
    
    return False

class Firefox_is_not_running(Exception): pass

'''
TODO
do we need to worry about clearing the clipboard after we put something on it?
'''
def get_URL():
    return _get_URL()

def _get_URL():
    if not _is_UI_up():
        raise Firefox_is_not_running()

    import pyautogui
    pyautogui.hotkey('ctrl', 'l') #select the address bar in firefox
    pyautogui.hotkey('ctrl', 'c') #copy the current URL
    pyautogui.hotkey('tab') #clear address bar selection

    import _util as util
    return util.get_clipboard()

class Cannot_load_URL(Exception): pass
class Bad_URL(Exception): pass

def go_to_URL(_url): return _go_to_URL(_url)

def _go_to_URL(_url):
    '''
    Enter a URL in Firefox, and wait for the URL to load
    Throwing on timeout
    '''
    import _util as util
    if not util.is_URL(_url):
        raise Bad_URL()

    if not _is_UI_up():
        raise Firefox_is_not_running()

    import pyautogui
    pyautogui.hotkey('ctrl', 'l') #select the address bar in firefox
    
    pyautogui.typewrite(str(_url)) #enter the URL
    
    pyautogui.hotkey('enter') #and go

    if not _is_page_loaded():
        raise Cannot_load_URL()

class Unknown_URL_Error(Exception): pass

def login_to_ezproxy():
    '''
    We try to login to ezproxy twice to confirm login
    '''

    if not _is_UI_up():
        raise Firefox_is_not_running()

    _first_login_attempt = False
    _second_login_attempt = False

    _first_login_attempt = _login_to_ezproxy()
    _second_login_attempt = _login_to_ezproxy()
    return all([_first_login_attempt, _second_login_attempt])

def _login_to_ezproxy(_additional_wait_time=None):
    '''
    Part of the process of fetching a research-work is to login to ezproxy
    so Zotero can proxy requests to different sites through the school's
    library access credentials


    to do this we need to login to: https://login.ezproxy.lib.ucalgary.ca/
    '''

    '''
    We might have to load as many as 3 pages, so set a timer for ~4
    page loads before giving up
    + additional wait time for retrying
    '''
    _wait_time = _page_load_timeout*4
    if not _additional_wait_time is None:
        _wait_time += _additional_wait_time
    
    import _util as util
    _timer = util.Timer( _wait_time )

    LOG.debug(f"Trying to go to: {'https://login.ezproxy.lib.ucalgary.ca/'}")

    _go_to_URL('https://login.ezproxy.lib.ucalgary.ca/')

    while True:
        '''
        It's hard to tell where we'll end up
        since the ezproxy landing page may redirect us
        so check for states of Firefox
        and act accordingly to what page we find ourself on
        '''

        #timeout after a few minutes
        if _timer.timed_out():
            LOG.debug("Failed to login to ezproxy")
            return False

        import time
        time.sleep(1)

        if not _is_page_loaded():
            raise Cannot_load_URL()

        _url = _get_URL()

        LOG.debug(f"Arrived at: {_url}")

        #if we're at: https://login.ezproxy.lib.ucalgary.ca/login
        #then we need to hit the log-in prompt to be prompted to sign-in with a username and password
        if ('login.ezproxy.lib.ucalgary.ca' in _url) and (str(_url).endswith("login")):
            LOG.debug("Saw https://login.ezproxy.lib.ucalgary.ca/login")

            import pyautogui
            pyautogui.click(447, 585, clicks=1, button='left')
            LOG.debug("Hit the sign in prompt.")

            continue
            
            #DEBUG
            #break

        #if we're at the sign-in screen (username and password prompt)
        #https://cas.ucalgary.ca/cas/ ...
        #then we should click the login button
        if "cas.ucalgary.ca" in _url:
            LOG.debug("Signing in with saved username and password")
            #then click where the sign-in button should be
            #even if it's not there, it doesn't matter since we're leaving this URL after this part
            import pyautogui
            pyautogui.click(837, 515, clicks=1, button='left')
        
            continue

            #DEBUG
            #break

        #if we're at this URL, then we've logged in
        #https://login.ezproxy.lib.ucalgary.ca/menu
        if ('login.ezproxy.lib.ucalgary.ca' in _url) and str(_url).endswith("menu"):
            LOG.debug("Saw https://login.ezproxy.lib.ucalgary.ca/menu")
            LOG.debug("We should be logged into the Ucalgary proxy")

            break

        LOG.debug(f"Arrived at unknown URL: {_url}")
        raise Unknown_URL_Error()

    return True

def is_zotero_connector_ready(_wait_time=None): return _is_zotero_connector_ready(_wait_time)

def _is_zotero_connector_ready(_wait_time=None):
    '''
    Keep checking the connector until we get at least two indications that
    the connector is ready in a row
    otherwise timeout
    '''
    if not _is_running_with_loaded_page():
        raise Firefox_is_not_running()

    _timer = None
    import _util as util
    if _wait_time is None:
        _timer = util.Timer( _page_load_timeout )
    else:
        _timer = util.Timer( _wait_time )

    _l_not_loaded_checks = []
    _l_loaded_checks = []

    while True:
        _l_not_loaded_checks.append( _zotero_connector_check_not_loaded() )
        _l_loaded_checks.append( _zotero_connector_check_loaded() )

        LOG.debug("Checks that Zotero Connector is ready:")
        LOG.debug(_l_not_loaded_checks)
        
        _enough_not_loaded_checks = (len(_l_not_loaded_checks) >= 2)
        _enough_loaded_checks = (len(_l_loaded_checks) >= 3)
        if _enough_not_loaded_checks and _enough_loaded_checks:
            _checks = []
            _checks.extend( _l_not_loaded_checks[-2:] )
            _checks.extend( _l_loaded_checks[-3:] )
            if all(_checks):
                LOG.debug("The Zotero connector is ready")
                return True

        if _timer.timed_out():
            LOG.debug("Timed out while waiting for Zotero connector to ready")
            return False

        import time
        time.sleep(1)

def _zotero_connector_check_not_loaded():
    '''
    take a screenshot of the region around the connector button
    and look for changes to indicate the connector is finished processing
    this is because the connector changes icon when it's finished
    '''
    from PIL import Image
    import imagehash
    reference_image_hash = imagehash.phash( Image.open( "/home/headless/bin/reference_zotero_connector.png" ) )

    from PIL import ImageGrab
    bbox = (1224, 96, 1360, 144)

    import imagehash
    latest_image_hash = imagehash.phash( ImageGrab.grab(bbox) )

    diff = abs(reference_image_hash - latest_image_hash)
    LOG.debug(f"Difference between connector reference image and current image: {diff}")

    if diff >= 20:
        return True
    return False

def _zotero_connector_check_loaded():
    '''
    Take a screenshot of the region around the connector button
    and compare that with several screenshots of the loaded connector
    checking for a match between them

    ----

    For some strange reason comparing these images is the opposite of what is
    expected
    The differences between the images gets LARGER when the connector is loaded
    rather than smaller

    2021-11-20 05:45:11,319; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 32 (correct)
    2021-11-20 05:45:11,319; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 32
    2021-11-20 05:45:11,320; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 28
    2021-11-20 05:45:11,321; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 32
    2021-11-20 05:45:11,321; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 34
    
    versus
    
    2021-11-20 05:45:17,644; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 34 (correct)
    2021-11-20 05:45:17,645; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 34
    2021-11-20 05:45:17,645; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 30
    2021-11-20 05:45:17,646; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 36
    2021-11-20 05:45:17,646; DEBUG [_firefox_handler:_zotero_connector_check_loaded] Difference: 38

    Thus we may as well use the sum of these values to try to indicate that
    the Connector is loaded
        the sums are 158 vs 172
    As the difference between the screenshot for the matching icon can't be
    distinguished from a false positive
    '''

    from PIL import Image
    import imagehash
    _connector_loaded_1 = imagehash.phash( Image.open( "/home/headless/bin/connector_loaded_1.png" ) )
    _connector_loaded_2 = imagehash.phash( Image.open( "/home/headless/bin/connector_loaded_2.png" ) )
    _connector_loaded_3 = imagehash.phash( Image.open( "/home/headless/bin/connector_loaded_3.png" ) )
    _connector_loaded_4 = imagehash.phash( Image.open( "/home/headless/bin/connector_loaded_4.png" ) )
    _connector_loaded_5 = imagehash.phash( Image.open( "/home/headless/bin/connector_loaded_5.png" ) )

    from PIL import ImageGrab
    bbox = (1224, 96, 1360, 144)

    import imagehash
    latest_image_hash = imagehash.phash( ImageGrab.grab(bbox) )

    _connector_loaded_images = [
        _connector_loaded_1,
        _connector_loaded_2,
        _connector_loaded_3,
        _connector_loaded_4,
        _connector_loaded_5,
    ]
    
    _sum = 0
    for i in range(len(_connector_loaded_images)):
        _sum += abs(_connector_loaded_images[i] - latest_image_hash)

    LOG.debug(f"Total sum of all differences between screenshots: {_sum}")

    if _sum > 165:
        return True
    return False

def click_zotero_connector(): return _click_zotero_connector()

def _click_zotero_connector():
    import pyautogui
    loc_zotero_button = [1295, 106]
    pyautogui.click(x=loc_zotero_button[0], y=loc_zotero_button[1], clicks=1, button='left')

class Cannot_login_to_EZProxy(Exception): pass

def Zotero_URL(
    _url,
    _additional_exproxy_login_time=None,
    _additional_connector_wait_time=None,
    _additional_connector_capture_time=None
    ):
    
    if not _is_running_with_loaded_page():
        start()

    _ezproxy_wait_time = 0
    if not _additional_exproxy_login_time is None:
        _ezproxy_wait_time += _additional_exproxy_login_time

    if not _login_to_ezproxy(_ezproxy_wait_time):
        raise Cannot_login_to_EZProxy()

    _go_to_URL(_url)

    _wait_time = 1
    while True:
        _connector_wait_time = _wait_time*_page_load_timeout
        if not _additional_connector_wait_time is None:
            _connector_wait_time += _additional_connector_wait_time

        if not _is_zotero_connector_ready(_connector_wait_time):
            _wait_time += 1
        else:
            break

        if _wait_time >= 3:
            LOG.debug("Timed out wait for Zotero connector")
            break

    _click_zotero_connector()

    '''
    Empirically, capturing page information with Zotero connector can take
    at most ~10 seconds
    but this may require more time if previous attempts did not return
    good information
    '''
    _capture_time = 10
    if not _additional_connector_capture_time is None:
        _capture_time += _additional_connector_capture_time

    import time
    time.sleep(_capture_time)

    _close()