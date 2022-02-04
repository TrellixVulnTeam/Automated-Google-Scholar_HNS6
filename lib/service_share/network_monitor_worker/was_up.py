import lib.logging as logging
LOG = logging.getLogger(__name__)

def _get_heartbeats(heartbeat_file):
    heartbeats = dict()
    import tarfile
    with tarfile.open(heartbeat_file, 'r') as tar:
        for tarinfo in tar:
            #heartbeats have the format: -1639960620.2999249
            #where the `-` indicates downtime, and a `+` indicates uptime
            #the number is a timestamp taken by time.time()
            _heartbeat = tarinfo.name
            _header = _heartbeat[0]
            _timestamp = _heartbeat[1:]

            import datetime
            _key = datetime.datetime.fromtimestamp(float(_timestamp))
            if _header == "+":
                _value = True
            else:
                _value = False

            heartbeats[_key] = _value

    return heartbeats

def _get_input():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("start")
    parser.add_argument("stop")
    args = parser.parse_args()

    return {"start": args.start, "stop": args.stop}

def _get_timeline(_heartbeats, start, stop):
    '''
    input a dict of heartbeats and output a list of True and False indicating
    uptimes and downtimes

    ----

    _heartbeats; a dict mapping datetime objects to boolean
        indicating uptime (True) and downtime (False)
        at the times indicated by the datetime objects
    start; a timestamp indicating the start time of a span of time we're interested
        in
    stop; a timestamp indicating the end of a span of time we're interested in
    '''
    heartbeats = _heartbeats.copy()

    #then insert the time values of start and stop into this sequence of heartbeats
    #so we can make an ordering of events
    #   marking start and stop with None values
    import datetime
    _start = datetime.datetime.fromtimestamp(float(start))
    _stop = datetime.datetime.fromtimestamp(float(stop))
    heartbeats[_start] = None
    heartbeats[_stop] = None

    #then sort by times to form a timeline of heartbeats showing uptime and
    #downtime; as well as showing where the start and stop times fell in the
    #timeline
    #   see:
    #   https://towardsdatascience.com/sorting-a-dictionary-in-python-4280451e1637
    heartbeats_sorted_by_time = sorted(heartbeats.items(), key = lambda kv: kv[0])

    #then discarding the times to only show a sequence of uptimes and downtimes
    return [t[1] for t in heartbeats_sorted_by_time]

def _partition_timeline(_timeline):
    #check for the empty case, where we have a timeline ONLY of the start and
    #stop events
    if all([(t is None)for t in _timeline]):
        res = {
            "pre_start": [],
            "post_stop": [],
            "between_start_and_stop": [],
        }

    timeline = _timeline.copy()

    #then removing and saving the uptimes and downtimes before start and after
    #stop
    #since we only want to check for downtime between start and stop
    #(except in the special case below)
    i_start = timeline.index(None)
    pre_start = timeline[0:i_start]
    timeline2 = timeline[i_start:]

    timeline2.reverse()

    j_stop = timeline2.index(None)
    post_stop = timeline2[0:j_stop]
    post_stop.reverse()
    timeline3 = timeline2[j_stop:]

    #then discarding the None's that mark start and stop,
    #to allow checking for any downtime (False values) in the span between
    #start and stop
    timeline3.pop(0)
    timeline3.pop(-1)
    
    res = {
        "pre_start": pre_start,
        "post_stop": post_stop,
        "between_start_and_stop": timeline3
    }

    return res

def _return(val):
    import json
    print( json.dumps( val ) )
    import sys
    sys.exit()

def main():
    log_path = "./log"
    archive_name = "heartbeats.tar"

    from pathlib import Path
    log_dir = Path(log_path)
    heartbeat_file = log_dir / archive_name
    
    heartbeats = _get_heartbeats(heartbeat_file)

    #BUG, in the rare case where we have 0 or 1 entries in the heartbeat file
    #just return as if we were connected
    if len(heartbeats) <= 1:
        _return(True)

    res = _get_input()
    start = res["start"]
    stop = res["stop"]

    timeline = _get_timeline(heartbeats, start, stop)
    res = _partition_timeline(timeline)

    #check for the special case if there is no gap between start and stop
    #this should produce an empty list
    if len(res["between_start_and_stop"]) == 0:
        '''
        In this special case, find the heartbeats immediately before the start
        time
        and
        after the stop time
        Then if they both show downtime, assume the span is downtime
        In the extra-special case that there are no heartbeats before
        or after the start and stop times, then assume downtime for each
        and return accordingly
        
        L, R neighbors

        T, T, assume up
        T, F, assume up
        F, T, assume up
        F, F, assume down
        and assume if there are no neighbors, that it's downtime; False
        '''
        pre_start = res["pre_start"]
        post_stop = res["post_stop"]

        LOG.debug("special case handling")

        _left_neighbor = False
        if len(pre_start) != 0:
            _left_neighbor = pre_start[-1]

        _right_neighbor = False
        if len(post_stop) != 0:
            _right_neighbor = post_stop[0]

        _return( _left_neighbor | _right_neighbor )

    #if there is any downtime in the span, then the network was not up during
    #the span marked by start and stop
    #and if there was no downtime, then the network was functioning during the
    #span
    _return( all(res["between_start_and_stop"]) )

if __name__ == '__main__': main()