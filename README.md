# Automated-Google-Scholar

## Overview

This project aims to automate downloading research-works with Google Scholar. The process begins with a search of Google Scholar. The search results in a list of URLs linking to research-works. The URLs are then "scraped" of content such that bibliographic information is captured and, commonly, files containing the content of the research-work are also captured. If the content of the research-work cannot be captured automatically, the troublesome URL is flagged for manual handling by the user.

This project attempts to fail-gracefully during the search of Google Scholar, attempting several different methods to capture Google Scholar search results. If no search results can be returned, then an informative error message is displayed. This approach was taken as extracting information from Google Scholar is commonly very difficult (Else, 2018; Haddaway et al., 2015; Martín-Martín et al., 2018).

This project also uses a novel approach of capturing the content of research-works. There are several reliable methods of automatically extracting information about research-works, but these tools tend to require user interaction. For example, Zotero, the software used in this project for this purpose, maintains a very well developed and stunningly comprehensive program for automatically extracting information related to research-works; But it is a browser plugin and only interacts with user mouse clicks. Thus, the approach used in this project attempts to automate such interactions via a virtual desktop.

## Purpose

Gathering knowledge is the cornerstone of research. For example, literature reviews, systematic reviews, or meta-analyses. They all have one thing in common: gathering and reviewing written works. Common tools to help with research are search engines. These search engines can search through large amounts of research-works automatically. One of the largest engines is Google Scholar. It can search an estimated 300 million documents (Gusenbauer, 2019). Using Google Scholar can be time-consuming and labour-intensive. Speeding up this process would be welcome addition to many researchers. However, automating research with Google Scholar is infamously difficult (Else, 2018; Haddaway et al., 2015; Martín-Martín et al., 2018). This project proposes to address that difficulty.

A poster on this project was presented at LSGSC 2021.

Mattingly, P. (2021, November 13–14). Automating research with Google Scholar [Conference presentation]. 2021 Learning Sciences Graduate Student Conference, Virtual. https://sites.google.com/view/lsgsc2021/home

## Technology Overview

This project is written in Python. As previously mentioned, several methods are used to conduct a search of Google Scholar for each query. These methods are: SerpAPI (1), ScrapingAnt (2), and Searx (3). These methods were chosen as they appeared to have robust methods for searching Google Scholar, and they can be controlled via Python; SerpAPI and ScrapingAnt have API libraries (4 & 5), while Searx can be "patched" to be used. Docker is used throughout to provide various functionalities (6); A Searx server is ran in a docker container, and the “virtual desktop” used for scraping is a docker container. Also, the “Network Monitor” class instantiates a docker container to monitor network traffic during sensitive operations. More specifically, the scraping aspect of the project, uses a docker container running Ubuntu (7 & 8). This container also has Firefox and Zotero installed to carry out the scraping. The scraping automation is done with the help of the `pyautogui` library (9).

1)	https://serpapi.com/
2)	https://scrapingant.com/
3)	https://searx.github.io/searx/
4)	https://github.com/serpapi/google-search-results-python
5)	https://github.com/ScrapingAnt/scrapingant-client-python
6)	https://www.docker.com/
7)	https://ubuntu.com/
8)	https://hub.docker.com/r/accetto/ubuntu-vnc-xfce-firefox-g3
9)	https://pyautogui.readthedocs.io/en/latest/

## Code Discussion

All of the shared code can be found in the `lib` directory. The main entry point for the program is in the `scraping` directory, specifically the `scraping_helper` module. This module allows a user to submit a query, which is then search for on Google Scholar, then all returned URLs are iterated over, and each research-work is attempted to be scraped for its content.

Other code is partitioned by purpose. Code having to do with searching Google Scholar is in the `search` directory. Classes that interact with Docker are in the `docker` directory.  Code for using Zotero to scrape research-work information is in `zoteroing`. The `service_share` directory contains files and directories intended to be shared with docker containers carrying out various functions in the program; see https://docs.docker.com/storage/volumes/. There are a few miscellaneous utility files in the root of `lib`; `exceptions` contains custom exceptions, `logging` contains logging infrastructure, `util` contains various utility functions. The `Network_Monitor_Helper` module contains functionality to launch a docker container to monitor network uptime during sensitive operations.

### lib.scraping
This sub-module contains two libraries: Scraping Helper and Scraping Tracker. Scraping Helper allows the user to input a query and various options to search Google Scholar for research-works matching the query, and then automatically attempting to fetch information about them. Scraping Helper requires the user to pass a string query, and a path to output the results to. Other options include the page of Google Scholar result to begin the process, and two dates that research-works should be published during; these options can be found on Google Scholar under their “since” and “until” options. Scraping Tracker is an internal library that keeps track of events that happen during execution; to support resuming an interrupted operation. Such events are: starting a page, finishing a page, starting to scrape a URL, and finishing with a URL. Such events are appended as text to a tar (1) archive, as such archives are resilient to malformed append operations that occur during an interrupted process. Then, given an interruption, such events can be read from the tar-archive to reconstruct where in the process the interruption occurred and resume that point.
1)	https://en.wikipedia.org/wiki/Tar_(computing)

### lib.search
This sub-module contains libraries related to methods of searching Google Scholar and their supporting functionality. The main entry-point for these libraries is the Search Helper library. This library iterates through the search methods defined in this sub-module (SerpAPI, ScrapingAnt, and Searx). Search Helper then returns the first set of URLs associated with a particular page of Google Scholar results. This approach was taken as it allows new methods of searching Google Scholar to be easily added; simply add an additional module and append it to the Search Helper library (the “_engines” variable) and the additional method will be included.
Each library in this sub-module is named after its titular method of searching Google Scholar. While the SerpAPI and ScrapingAnt modules libraries are wrappers around their respective API library’s, Searx bears closer examination. Searx is an open-source search engine (1). The Searx search engine does support searching Google Scholar by default, but it does not allow for the full range of options needed to full search Google Scholar in keeping with this program. Specifically, it does not support the “since” and “until” options as other methods do. To resolve this the Searx server is “patched” to allow these options to be passed to Google Scholar. More specifically Searx defines its server’s behaviour through so-called “engines”; see (2). These engines are Python files that use their internal API to carry out the specifics of a search. Thus, to modify the Google Scholar Searx engine, a modified engine file is applied to the server after it is started in Docker; see: `lib/service_share/searx_worker/google_scholar.py` for the modified file.
1)	https://searx.github.io/searx/
2)	https://github.com/searx/searx/blob/master/searx/engines/google_scholar.py

### lib.zoteroing
This module contains libraries for managing the automation of Zotero and scraping URLs retrieved from searching Google Scholar; “Zotero” and “scraping” can be called “Zoteroing”. The main entry point for this module is the Zotero_Helper library. The main function in this library (start) takes an iterable of URLs and an output directory to save the results of Zoteroing into. The process of Zoteroing begins by parceling work on URLs among several “workers”. Each worker in this context is a single instance of a Docker container in swarm mode. Docker swarm mode (1) can roughly be thought of as several processes executing in parallel, but instead of process each unit of work (“worker”) is executed by a Docker container. A Docker container is similar to a virtual machine in that it executes an encapsulated/containerized environment that carries out a task. In this case each task is the process of Zoteroing within a “virtual desktop” Docker container. In this case the encapsulated virtual environment within the Docker container is an Ubuntu desktop running software for Zoteroing. More detail on the Zoteroing process is discussed below. Once each worker is completes its task of scraping information related to a URL with Zotero, it is shutdown and a new URL is processed with a new worker in its place. Once all URLs have been processed, then the results data is cleaned by removing excess files compiled during the Zoteroing process. This data is also then analyzed in order to assess success or failure of each Zoteroing operation. URLs associated with failed Zoteroing operations are compiled into a “report” so that each such URL can be manually processed by the user; The report is a simple HTML table listing the URLs that had issues during the Zoteroing process.

This module also contains an internal library named _zoteroing_output_helper which provides various helper functions for dealing with the output of the Zoteroing. For example, there are functions for cleaning the data, finding data associated with failed Zoteroing operations, etc.
1)	https://docs.docker.com/engine/swarm/

#### The Zoteroing process

## References

Gusenbauer, M. (2019). Google Scholar to overshadow them all? Comparing the sizes of 12 academic search engines and bibliographic databases. Scientometrics, 118(1), 177–214. https://doi.org/10.1007/s11192-018-2958-5

Else, H. (2018). How I scraped data from Google Scholar. Nature. https://doi.org/10.1038/d41586-018-04190-5

Haddaway, N. R., Collins, A. M., Coughlin, D., & Kirk, S. (2015). The Role of Google Scholar in Evidence Reviews and Its Applicability to Grey Literature Searching. PLOS ONE, 10(9), e0138237. https://doi.org/10.1371/journal.pone.0138237

Martín-Martín, A., Costas, R., van Leeuwen, T., & López-Cózar, E. D. (2018). Evidence of Open Access of scientific publications in Google Scholar: A large-scale analysis [Preprint]. SocArXiv. https://doi.org/10.31235/osf.io/k54uv
