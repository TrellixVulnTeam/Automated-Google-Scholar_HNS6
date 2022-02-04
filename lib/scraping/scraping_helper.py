import lib.logging as logging
LOG = logging.getLogger(__name__)

def start(query, output, start_page=1, stop_page=50, _since=None, _until=None):
    import lib.util as util
    if not util.is_int(start_page):
        raise exp.Bad_argument(f"Argument `start_page` should be integer.")

    if not util.is_int(stop_page):
        raise exp.Bad_argument(f"Argument `stop_page` should be integer.")

    if not (1 <= start_page <= 50):
        raise exp.Bad_argument(f"Argument `start_page` should be between 1 and 50.")

    if not (1 <= stop_page <= 50):
        raise exp.Bad_argument(f"Argument `stop_page` should be between 1 and 50.")

    if not (start_page <= stop_page):
        raise exp.Bad_argument(f"Argument `start_page` should precede `stop_page`.")

    return _start(query, output, start_page, stop_page, _since, _until)

def _start(query, output, start_page=1, stop_page=50, _since=None, _until=None):
    compiled_results = []
    for i in range(start_page, stop_page+1):
        import lib.search.search_helper as sh
        urls = sh.search(query, page=i, since=_since, until=_until)

        #if we've finished our search, then return with final statistics
        if len(urls) == 0:
            return _finish_up( compiled_results )

        import lib.Zoteroing_Helper as zh
        res = zh.start(urls, _output_dir(output))

        compiled_results.append( res )

def _output_dir(_dir):
    from pathlib import Path
    path = Path(_dir)

    if not path.exists():
        path.mkdir()
    
    raw_dir = path / "_raw"

    if not raw_dir.exists():
        raw_dir.mkdir()

    return str(raw_dir)

def _finish_up(results):
    print(results)