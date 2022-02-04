import lib.logging as logging
LOG = logging.getLogger(__name__)

r'''
This code runs continuously to monitor network connection
logging uptime and downtime to a "heartbeat" file

The heartbeat file is kept in the "log" directory inside the container
and the "log" directory maps to a temporary dir, so that it's removed when
the container is stopped

The idea is to startup a container running this code when running an operation
that is sensitive to network disruption
    like searching, or Zoteroing
Then, after the monitored operation is complete, this container can be queried
to see if there were any network interruptions during the span of time
the operation was completing
    see:
    C:\Users\pmatt\Documents\Professional Work\Work\dev\dev, scraping\dev\lib\service_share\network_monitor_worker
    was_up.py

----

The simplest means of tracking network connection seems to be to append
uptimes/downtime to a file
    since we may get interruptions in monitoring unpredictably
something that is stable for interrupts is tar
we can open an archive for appending and append a new file
    where we include information in the file pertinent to the heartbeat
then if we're interrupted, we can find the last completely appended record
and remove the corrupted ones
and the archive is still be valid
    see:
    https://stackoverflow.com/questions/4764824/tar-archive-how-reliable-is-append
'''

def main():
    log_path = "./log"
    archive_name = "heartbeats.tar"

    from pathlib import Path
    log_dir = Path(log_path)

    if not log_dir.exists():
        log_dir.mkdir()

    heartbeat_file = log_dir / archive_name
    if not heartbeat_file.exists():
        heartbeat_file.touch()

        #make an empty tar archive
        #see: https://bugs.python.org/issue6123
        #https://superuser.com/questions/448623/how-to-get-an-empty-tar-archive
        #https://docs.python.org/3/library/tarfile.html#tarfile.TarInfo
        import tarfile
        content = tarfile.TarInfo()
        tar = tarfile.open(heartbeat_file, mode="w", tarinfo=content)
        tar.close()

    while True:
        import tarfile
        with tarfile.open(heartbeat_file, 'a') as tar: #appending to the archive
            #write out a temporary file that we can name
            #the name is a timestamp from time.time()
            #we can then read in those file names, parse them, and
            #determine when the faults occured
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                from pathlib import Path
                pth = Path(td)
                
                import time
                hearbeat = time.time()

                #add a simple signifier to note if the network was up or down
                #during this heartbeat
                import lib.util as util
                if util.network_connected():
                    LOG.debug("Logging heartbeat of network UPtime")
                    hearbeat = f"+{hearbeat}"
                else:
                    LOG.debug("Logging heartbeat of network DOWNtime")
                    hearbeat = f"-{hearbeat}"

                #name the temporary file to the heartbeat
                tmp_file = pth / hearbeat
                tmp_file.touch()

                tar.add( tmp_file, arcname=tmp_file.name )

        import time
        time.sleep(1)

if __name__ == '__main__':
    main()