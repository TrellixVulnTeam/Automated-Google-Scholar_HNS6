import logging
LOG = logging.getLogger(__name__)

#_log_dir = "/home/headless/tmp/"
#_log_dir

def _close():
    import _zotero_handler as zh
    import _firefox_handler as fh
    fh.close()
    zh.close()

def _pre_run_cleanup():
    _close()

    import _zotero_handler as zh
    zh.cleanup_export()

    import _firefox_handler as fh
    fh.logs_cleanup()

def _get_input():
    #capturing the URL argument
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    return args.url

'''
TODO
If we're having trouble logging into ezproxy, then we may just want to skip
that step, and then attempt the rest of the steps without it
rather than attempting to wait for ezproxy and failing out if we can't login
'''
def main():
    target_url = _get_input()
    
    #keep track of the number of runs that failed because correctable issues
    #occured; The most common being work with Zotero connector and waiting
    #for it to gather good information from the URL about the research-work
    _bad_run = 0
    _additional_wait_times = [0, 1*60, 2*60, 5*60]
    while True:
        #if there are too many bad runs, then give up and return what we have
        if _bad_run >= 3:
            LOG.debug("Too many bad runs, giving up")
            break

        _pre_run_cleanup()

        #open Zotero to capture output from the Zotero connector in Firefox
        import _zotero_handler as zh
        zh.start()

        #use Firefox to capture the content from the URL that contains a research-work
        #if there bad previous runs, then wait for the Zotero connector 
        #and potentially ezproxy
        #for longer spans, until we succeed or have to give up
        import _firefox_handler as fh
        try:
            fh.Zotero_URL(
                target_url,
                _additional_exproxy_login_time = _additional_wait_times[_bad_run],
                _additional_connector_wait_time = _additional_wait_times[_bad_run],
                _additional_connector_capture_time = _additional_wait_times[_bad_run],
                )
        except fh.Unknown_URL_Error:
            LOG.debug("Unknown_URL_Error")
            LOG.debug("Couldn't load a URL with Firefox for some reson, retrying")

            #if we hit an uncrecoverable error, then just try again
            continue
        except fh.Cannot_login_to_EZProxy:
            LOG.debug("Cannot_login_to_EZProxy")
            LOG.debug("Couldn't loging to EZproxy, Retrying")

            _bad_run += 1
            continue

        #then export what was captured with Zotero to see if we want to retry
        #the capture for better quality output
        import _zotero_handler as zh
        try:
            _export = zh.export()
        except zh.Previous_export_found:
            LOG.debug("Found an existing export directory; This will interefere with exporting")
            LOG.debug("Retrying")

            continue
        except zh.Export_files_do_not_exist:
            LOG.debug("Some issue prevented files being exported from Zotero")
            LOG.debug("Retrying")

            continue
        except zh.Zotero_not_ready:
            LOG.debug("Could not work with Zotero to export")
            LOG.debug("Retrying")

            continue

        _entries = zh.get_export_entry_types(_export)

        LOG.debug("Got export from Zotero")

        _have_entries = (len(_entries) > 0)
        _have_bad_entries = ("misc" in _entries)
        _more_than_one_entries = (len(_entries) > 1)

        #check that we got some entries, otherwise retry
        if not _have_entries:
            LOG.debug("No entries seen this run; Retrying")
            _bad_run += 1
            continue

        if _have_entries:
            if _have_bad_entries and _more_than_one_entries:
                LOG.debug("Found export with good bib information, exiting")
                break

            if not _have_bad_entries:
                LOG.debug("Found export with good bib information, exiting")
                break

            #a "misc" entry from Zotero means that Zotero doesn't have good
            #bib information about a research-work
            #so we need to try again, but this time we have to wait longer
            #for the connector to load, so we can try to get good information
            #from the URL about the research-work
            if _have_bad_entries and (not _more_than_one_entries):
                LOG.debug("Found export, but with bad bib information; Retrying")
                _bad_run += 1
                continue

    _close()

    #sometimes we have issues with getting all of the logs, so cleanup again here
    import _firefox_handler as fh
    fh.logs_cleanup()

    #and writeout some information about this process
    d_ret = {
        "URL": target_url,
        "error": False,
        "error msg": None,
    }

    _failed_out = (_bad_run >= 3)
    if _failed_out:
        d_ret["error"] = True
        d_ret["error msg"] = "Failed due to too many bad runs"

    import _zotero_handler as zh
    
    _export = zh.get_path_to_export()
    _export_exists = (not _export is None)

    if not _export_exists:
        d_ret["error"] = True
        d_ret["error msg"] = "Failed due to unknown export issue"

    if (not _failed_out) and (_export_exists):
        d_ret["Exported library"] = _export

    from pathlib import Path
    import json
    Path(_log_dir + "/info.json").write_text( json.dumps( d_ret ) )

def _setup_logging():
    #do we have a log directory?
    from pathlib import Path
    log_dir = Path(_log_dir).resolve()

    if not log_dir.exists():
        log_dir.mkdir()

    #and setup the log file to open with utf-8 encoding
    import logging
    from pathlib import Path
    str_path_log_file = str(log_dir / (str(Path(__file__).name) + '.log') )
    kwds = {'filename': str_path_log_file,'mode':'a', 'encoding':'utf-8'}

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
            logging.FileHandler( **kwds ),
            logging.StreamHandler(),
        ]
    )

if __name__ == '__main__':
    #TODO, make this more robust and with proper access
    #first, generate a unique path to use for the tmp directory, as it's
    #shared with other processes
    import uuid
    from pathlib import Path
    log_dir = Path("/home/headless/tmp/" + str(uuid.uuid4()))
    log_dir.mkdir()
    global _log_dir
    _log_dir = str(log_dir)

    import _firefox_handler as fh
    #default /home/headless/tmp/
    fh._log_dir = str(log_dir)

    import _zotero_handler as zh
    #default '/home/headless/tmp/My Library'
    zh._export_path = str( log_dir / 'My Library' )

    _setup_logging()

    import time
    start_time = time.time()

    main()

    LOG.debug(f"Time: --- {(time.time() - start_time)} seconds ---")