r'''
Motivation
    given a query string, fetch the URLs from a single page of Google Scholar
    
    Each page of Scholar is scraped by one of three methods
        whichever method returns information first is used
    These methods are (in order): Searx, SerpAPI, and ScrapingAnt
        see:
        https://searx.me/
        https://serpapi.com/
        https://scrapingant.com/
'''

import lib.logging as logging
LOG = logging.getLogger(__name__)

import lib.search.ScrapingAnt_helper as ScrapingAnt_helper
import lib.search.Searx_Helper as Searx_Helper
import lib.search.SERP_API_helper as SERP_API_helper
_engines = [Searx_Helper, SERP_API_helper, ScrapingAnt_helper]

def search(query, page=1, since=None, until=None):
    '''
    Conduct a search for Google Scholar results over the existing search engines
    monitor network connection while searching
    if there's an issue with the network connection during the search
    then block until the network comes back up and retry
    '''
    import lib.search._search_input_validator as SIV
    params = SIV.validate(query, page, since, until)

    for engine in _engines:
        res = _try_engine(engine, params)

        #then, if there were results and no other issues, then return the results
        #otherwise, try the next engine
        if len(res) != 0:
            return res

    #then if we've exhausted the engines, and they all returned without incident
    #but no results were obtained, then return empty
    return []

def _try_engine(engine, params):
    while True:
        import lib.util as util
        if util.network_connected():
            LOG.debug("Starting search")
            #start network montioring
            from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
            _nmh = NMH()
            _nmh.start()

            LOG.debug("network monitoring started")

            #start the search process with the search engine
            res = None
            try:
                res = engine.search( **params )
                LOG.debug("search completed successfully")
            except:
                #on an exception from the search engine, stop network monitoring
                #check for interruptions
                LOG.debug("saw an exception during the search")

                network_was_up = _nmh.stop()

                #if the network was up during the search, then raise whatever
                #exception was thrown
                #otherwise, retry with the same search engine once the network
                #is back up
                if network_was_up:
                    LOG.debug("network was up during search, so raising")
                    raise

            if not res is None:
                #then if the search completed without exception, check for network
                #issues again
                #if there were some during the search
                #then retry the search when the network is up
                LOG.debug("checking for network issues in an otherwise successful search")
                network_was_up = _nmh.stop()
                if network_was_up:
                    LOG.debug("fully successful search!")
                    return res

                LOG.debug("network problems during search, retrying")
        else:
            LOG.debug("Network not connected, waiting...")

        import time
        time.sleep(1)