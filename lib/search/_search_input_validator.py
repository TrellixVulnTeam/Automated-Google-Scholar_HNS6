import lib.logging as logging
LOG = logging.getLogger(__name__)

def validate(query, page=1, since=None, until=None):
    '''
    Verify some standard search parameters and return a params object
    that can be used by other search engines
    '''

    import lib.util as util
    if not util.is_valid_page_number(page):
        import lib.exceptions as exp
        msg = "`page` argument should be integer between 1 and 50."
        raise exp.Bad_argument(msg)

    import lib.util as util
    if (not since is None) and (not util.is_valid_year(since)):
        import lib.exceptions as exp
        msg = "`since` argument should be integer or None."
        msg += "The argument should be a year between 1 and the current year."
        raise exp.Bad_argument(msg)

    import lib.util as util
    if (not until is None) and (not util.is_valid_year(until)):
        import lib.exceptions as exp
        msg = "`until` argument should be integer or None."
        msg += "The argument should be a year between 1 and the current year."
        raise exp.Bad_argument(msg)
    
    import lib.util as util
    if (not since is None) and (not until is None):
        if (not util.are_valid_search_years(since, until)):
            import lib.exceptions as exp
            msg = "`since` and `until` arguments should be years such that "
            msg += "since <= until."
            raise exp.Bad_argument(msg)

    _ret = {"query": str(query), "page": page}
    
    if (not since is None):
        _ret["since"] = since

    if (not until is None):
        _ret["until"] = until

    return _ret