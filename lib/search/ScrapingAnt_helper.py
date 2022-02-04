import lib.logging as logging
LOG = logging.getLogger(__name__)

def search(query, page=1, since=None, until=None):
    SAH = ScrapingAnt_helper(query, page, since, until)
    return SAH.run()

class ScrapingAnt_helper:
    def __init__(self, query, page=1, since=None, until=None):
        self._key = '' #TODO, set by user

        import lib.search._search_input_validator as SIV
        self._params = SIV.validate(query, page, since, until)

        self._last_proxy_country = None

    def run(self):
        url = self._get_query_string(self._params)
        
        '''
        Scholar will occasionally not return content
        in this case the query is being blocked
        so just retry with a new proxy
        and
        wait a random amount of time (up to ~10 minutes)
        for the query to give results
        '''
        for wait_time in range(1, 12+1):
            pc = self._choose_proxy_country()
            html = self._search(url, pc)
            links = self._parse(html)

            if len(links) == 0:
                LOG.debug("Saw zero results, retrying...")
                import random
                _current_wait_time = random.normalvariate( (wait_time**2), 1)
                LOG.debug(f"Waiting time: {_current_wait_time}")

                import time
                time.sleep( _current_wait_time )
            else:
                return links
        
        msg = "No results were returned,"
        msg += " "
        msg += "even after multiple searches and timing out."
        import lib.exceptions as exp
        raise exp.search.Failed_Search(msg)
    
    def _get_query_string(self, params):
        d_query = {
            "start": (params["page"] - 1)*20,
            "q": params["query"],
            "hl": "en",
            "as_sdt": "0,5",
        }

        if "since" in params:
            d_query["as_ylo"] = params["since"]

        if "until" in params:
            d_query["as_yhi"] = params["until"]

        #turn the query object into a query string
        #see: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode
        #https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python
        import urllib
        base_url = 'https://scholar.google.com/scholar?'
        return str(base_url + urllib.parse.urlencode(d_query, safe=','))

    def _choose_proxy_country(self):
        while True:
            import random
            _pc = random.choice( ['BR',
                'CZ', 'FR', 'DE', 'HK',
                'IT', 'IL', 'JP',
                'NL', 'ES', 'US'] )

            if _pc != self._last_proxy_country:
                self._last_proxy_country = _pc
                return _pc

    def _search(self, url, _pc):
        '''
        Use ScrapingAnt to return the raw HTML form a page from Google Scholar
        then parse that content for the links we're interested in
        '''

        import scrapingant_client
        client = scrapingant_client.ScrapingAntClient(token=self._key)
        
        #for the exceptions see:
        #https://github.com/ScrapingAnt/scrapingant-client-python
        #and
        #https://github.com/ScrapingAnt/scrapingant-client-python/blob/master/scrapingant_client/errors.py
        try:
            return client.general_request(url, proxy_country=_pc).content
        except scrapingant_client.ScrapingantClientException as e:
            import lib.exceptions as exp
            raise exp.search.Failed_Search(e)
        '''
        except scrapingant_client.ScrapingantInvalidTokenException:
            msg = "The API token is wrong or"
            msg += " "
            msg += "you have exceeded the API calls request limit"
            import lib.exceptions as exp
            raise exp.search.Failed_Search(msg)
        except scrapingant_client.ScrapingantInvalidInputException as e:
            msg = "Invalid value provided."
            msg += " "
            msg += "Please, look into error message for more info."
            msg += "\n"
            msg += str(e)
            import lib.exceptions as exp
            raise exp.search.Failed_Search(msg)
        except scrapingant_client.ScrapingantInternalException:
            msg = "Something went wrong with the server side code."
            msg += " "
            msg += "Try again later or contact ScrapingAnt support."
            import lib.exceptions as exp
            raise exp.search.Failed_Search()
        except scrapingant_client.ScrapingantSiteNotReachableException:
            msg = "The requested URL is not reachable. Please, check it locally"
            raise exp.search.Failed_Search(msg)
        '''

    def _parse(self, html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, features="lxml")

        #find all the H3 tags, they seem to hold the links for the individual papers
        #then find all link (a) tags, and then the href properties inside those links
        #see:https://stackoverflow.com/questions/36187731/python-beautifulsoup-get-specific-element
        #https://stackoverflow.com/questions/46933679/scraping-text-in-h3-and-div-tags-using-beautifulsoup-python
        #https://stackoverflow.com/questions/32179609/how-to-get-link-of-h3-in-a-website-with-beautfulsoup4
        l_ret = list()
        for i in soup.find_all('h3'):
            for j in i.find_all('a'):
                l_ret.append(j.get('href'))

        return l_ret