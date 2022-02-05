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

All of the code can be found in the `lib` directory. The main entry point for the program is in the `scraping` directory, specifically the `scraping_helper` module. This module allows a user to submit a query, which is then search for on Google Scholar, then all returned pages are iterated over, and each research-work is attempted to be scraped for its content.

Other code is partitioned by purpose. Code having to do with searching Google Scholar is in the `search` directory. Classes that interact with Docker are in the `docker` directory.  Code for using Zotero to scrape research-work information is in `zoteroing`. The `service_share` directory contains files and directories intended to be shared with docker containers carrying out various functions in the program; see https://docs.docker.com/storage/volumes/. There a few miscellaneous utility files in the root of `lib`; `exceptions` contains custom exceptions, `logging` contains logging infrastructure, `util` contains various utility functions. The `Network_Monitor_Helper` module contains functionality to launch a docker container to monitor network uptime during sensitive operations.

## References

Gusenbauer, M. (2019). Google Scholar to overshadow them all? Comparing the sizes of 12 academic search engines and bibliographic databases. Scientometrics, 118(1), 177–214. https://doi.org/10.1007/s11192-018-2958-5

Else, H. (2018). How I scraped data from Google Scholar. Nature. https://doi.org/10.1038/d41586-018-04190-5

Haddaway, N. R., Collins, A. M., Coughlin, D., & Kirk, S. (2015). The Role of Google Scholar in Evidence Reviews and Its Applicability to Grey Literature Searching. PLOS ONE, 10(9), e0138237. https://doi.org/10.1371/journal.pone.0138237

Martín-Martín, A., Costas, R., van Leeuwen, T., & López-Cózar, E. D. (2018). Evidence of Open Access of scientific publications in Google Scholar: A large-scale analysis [Preprint]. SocArXiv. https://doi.org/10.31235/osf.io/k54uv
