import lib.logging as logging
LOG = logging.getLogger(__name__)

_serpAPI_key = "" #TODO, set by user

def search(query, page=1, since=None, until=None):
    return _SERP_API_search(query, page, since, until)

def _SERP_API_search(query, page=1, since=None, until=None):
    import lib.search._search_input_validator as SIV
    res = SIV.validate(query, page, since, until)

    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": str(_serpAPI_key),
        "start": ((page - 1)*20)
    }

    if "since" in res:
        params["as_ylo"] = res["since"]

    if "until" in res:
        params["as_yhi"] = res["until"]

    from serpapi import GoogleSearch
    res = GoogleSearch(params).get_dict()

    #checking for errors in the search process
    import lib.exceptions as exp
    _msg = f"SERP API search failed with result: {res}"
    if len(res.keys()) == 0:
        raise exp.search.Failed_Search(_msg)

    if not "search_metadata" in res:
        raise exp.search.Failed_Search(_msg)

    if not "status" in res["search_metadata"]:
        raise exp.search.Failed_Search(_msg)

    #checking if search was successful or not
    if not res["search_metadata"]["status"] == "Success":
        LOG.debug(f"Search status showed an issue with the search:")
        LOG.debug(f'{res["search_metadata"]["status"]}')
        return []

    #then checking for results returned from the search
    if 'organic_results' in res:
        LOG.debug(f"SERP API returned some results")
        return [str(r["link"]) for r in res['organic_results'] if "link" in r]

    #otherwise, there wasn't an issue with the search
    #and the search was successful
    #but there were no results to return
    return []