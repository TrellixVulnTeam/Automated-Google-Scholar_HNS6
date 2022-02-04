'''
Motivation

A set of helper functions for working with the output of the Zoteroing process
Notes on what individual functions do are noted in each function
The class takes an argument of a folder that contains Zoteroing output to query
    The `pth` argument can be the parent directory of a directory that holds
    Zoteroing output
'''
#TODO, testing
import lib.logging as logging
LOG = logging.getLogger(__name__)

class _zoteroing_output_helper:
    '''
    info.json format:
    {
    "URL": "https://science.sciencemag.org/content/368/6490/489.abstract", 
    "error": false,
    "error msg": null,
    "Exported library": "/home/headless/tmp/29ff765b-b2fc-44b8-9822-20875620478b/My Library"
    }
    '''
    def __init__(self, pth):
        import lib.util as util
        if not util.is_valid_path(pth):
            import lib.exceptions as exp
            raise exp.Bad_argument(f"Bad path: {pth}")

        from pathlib import Path
        self._output_path = Path(pth)

    def has_output(self): return self._has_output(self._output_path)

    def _has_output(self, pth):
        '''
        Check if there's Zoteroing output at pth
        '''
        if len(self._info_json_paths_and_content(pth)) > 0:
            return True
        return False

    def _info_json_paths_and_content(self, pth):
        '''
        Return a dict() with keys that are the paths to info.json files
        detected at pth
            these files hold information about the output of Zoteroing
        The values are the parsed (JSON) content of these files
        '''
        from pathlib import Path
        path = Path(pth)
        
        paths_to_content = {}
        for f in path.rglob("*"):
            if f.is_file() and (f.name == "info.json"):
                import json
                from pathlib import Path
                content = json.loads( f.read_text() )

                paths_to_content[str(f)] = content

        return paths_to_content

    def is_URL_done(self, url): return self._is_URL_done(url, self._output_path)
    
    def _is_URL_done(self, url, pth):
        '''
        Given a URL, this function checks through all of the info.json files
        present in pth and tries to find a match
        This implies that the Zoteroing process is complete for that URL
        '''
        p2c = self._info_json_paths_and_content(pth)
        for content in p2c.values():
            if ("URL" in content) and (content["URL"] == str(url)):
                return True
        return False

    def get_finished_URLs(self):
        return self._get_finished_URLs(self._output_path)
    
    def _get_finished_URLs(self, pth):
        '''
        Check all of the info.json files in the Zoteroing output directory
        and return all of their URLs
        This should show which URLs have completed Zoteroing
        '''
        p2c = self._info_json_paths_and_content(pth)
        res = []
        for content in p2c.values():
            res.append( content["URL"] )

        return res

    def content(self): return self._content(self._output_path)

    def _content(self, pth):
        '''
        Return just the parsed content of all info.json files in the Zoteroing
        output directory
        '''
        p2c = self._info_json_paths_and_content(pth)
        return [c for c in p2c.values()]

    def paths(self): return self._paths(self._output_path)

    def _paths(self, pth):
        '''
        Return just the paths to all the info.json files in the Zoteroing
        output directory
        '''
        p2c = self._info_json_paths_and_content(pth)
        return [p for p in p2c.keys()]

    def paths_and_content(self):
        return self._info_json_paths_and_content(self._output_path)

    def get_bibtex(self): return self._get_bibtex(self._output_path)

    def _get_bibtex(self, pth):
        '''
        After parsing information from the Zoteroing output directory
        return all the bibtex information cotained in `My Library.bib` files
        in that directory
            as Bibtex is dumped by the Zoteroing process depending on
            what research-works were retrieved during the Zoteroing process
            (into `My Library.bib`)
        Returning a mapping between the URL that was Zoteroed and the bibtex

        --

        A URL is mapped to None in instances where no Bibtex file could be found
        or no bibtext output could be parsed
        '''
        u2fb = self._get_bibtex_and_files(self._output_path)

        res = {}
        for (url, fb) in u2fb.items():
            if (not u2fb[url] is None) and "bibtex" in u2fb[url]:
                res[url] = u2fb[url]["bibtex"]
            else:
                res[url] = None
        return res

    def get_files(self): return self._get_files(self._output_path)
    
    def _get_files(self, pth):
        '''
        After parsing information from the Zoteroing output directory
        return paths to the files downloaded during the Zoteroing process
            The files related to research-works were retrieved during the
            Zoteroing process
        '''
        u2fb = self._get_bibtex_and_files(pth)

        res = {}
        for (url, fb) in u2fb.items():
            if (not u2fb[url] is None) and "files" in u2fb[url]:
                res[url] = u2fb[url]["files"]
            else:
                res[url] = None
        return res
    
    #---------------------------------------------------------------------------
    def _get_bibtex_and_files(self, pth):
        '''
        Given a path to Zoteroing output
        Find the folders named "My Libray"
            which contains the output of Zotero's exporting
        In this directory return the path of the bibtex file for parsing
            "My Libray.bib"
        Once the bibtex is parsed, find the paths to files within the "My Library"
        directory from it
        and return a dict that maps URL's found in the output to the bibtex
        and file paths associated with them
            that is, a Zoteroed URL should (ideally) output both bibtex and
            files as a result of its process
            Where the bibtex describes information about the research-works
            in the files
            If there are no bibtex or files, then the Zoteroing process may
            have failed
        Finally, at times the Zoteroing process may return "snapshot" files
        of pages related to Zoteroing works; These files are not returned
            Where snapshot files are simple HTML files that are saved
            from the pages where Zoteroing was done
        '''
        res = {}
        p2c = self._info_json_paths_and_content(pth)

        for (path, content) in p2c.items():
            url = content["URL"]
            
            from pathlib import Path
            _info_json_path = Path(path).resolve()

            my_library_path = _info_json_path.parent / "My Library"

            bibtex = self._get_bibtex_from_path( _info_json_path.parent )

            res[url] = None

            if not bibtex is None:
                import bibtexparser
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = bibtexparser.loads( bibtex, parser=parser)

                for _entry in bib_database.entries:
                    if ('file' in _entry) and isinstance(_entry["file"], str):
                        '''
                        The raw entry can look like this:
                        Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html
                        
                        Note there are multiple file descriptors
                        and each descriptor has multiple parts
                        '''

                        #then we can split each entry into individual file descriptors:
                        #['Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf', 'ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html']
                        _file_descriptors = _entry["file"].split(";")

                        #then for each descriptor, we can split it into its
                        #component parts:
                        #['Full Text', 'files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf', 'application/pdf']
                        #['ScienceDirect Snapshot', 'files/3/S0924857920300674.html', 'text/html']
                        for _descriptor in _file_descriptors:
                            _parts = _descriptor.split(":")

                            #then note that some parts are file paths:
                            #'files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf'
                            #'files/3/S0924857920300674.html'
                            #with each path being under:
                            #[output directory]/My Library/
                            #e.g., [output directory]/My Library/files/3/S0924857920300674.html
                            #so if we join the path from the output directory
                            #with My Library/[parts], and test to see if they
                            #exist, we can find full paths to the files
                            for _part in _parts:
                                _file_path = self._is_bibtext_string_a_path_to_file(my_library_path, _part)
                                if not _file_path is None:
                                    #skipping snapshots
                                    if not self._is_file_a_snapshot(_file_path):
                                        if res[url] is None:
                                            res[url] = {"bibtex": bibtex, "files": []}
                                        from pathlib import Path
                                        res[url]["files"].append( str( Path(_file_path).resolve() ) )
                        #end: for _descriptor in _file_descriptors:
                    #end: if ('file' in _entry) and isinstance(_entry["file"], str):
                #end: for _entry in bib_database.entries:
            #end: if not bibtex is None
        #end: for (path, content) in p2c.items()

        return res
    
    def _is_bibtext_string_a_path_to_file(self, root, string):
        '''
        Helper function for _get_bibtex_and_files()
        '''
        from pathlib import Path
        _possible_file_path = (Path(root) / string)

        try:
            file_exists = _possible_file_path.exists()
        except OSError: #check for strings that are bad file names
            pass
        else:
            if file_exists:
                return _possible_file_path.resolve()

        return None

    def _is_file_a_snapshot(self, path):
        '''
        Helper function for _get_bibtex_and_files()
        '''
        from pathlib import Path
        _path = Path(path)
        return ("htm" in _path.suffix)
    #---------------------------------------------------------------------------

    def _get_bibtex_from_path(self, pth):
        '''
        Given a path to an instance of Zoteroing output, find and return
        the content of the "My Library.bib" file in that directory
        or None if it can't be found
            no bibtex is parsed, rather the raw string is returned
        '''
        from pathlib import Path
        my_library = Path(pth) / "My Library"

        #raise Exception(my_library)

        #by default set the value to None if there's some error with the
        #bibtex file
        res = None

        if my_library.exists():
            my_library_bib = my_library / "My Library.bib"

            if my_library_bib.exists():
                res = str( my_library_bib.read_text() )

        return res

    def URLs_need_manual_handling(self):
        return self._URLs_need_manual_handling(self._output_path)

    def _URLs_need_manual_handling(self, pth):
        '''
        Given a path to Zoteroing output, check info.json files for signs of
        errors
        and then flag those URLs for manual processing
        and
        also check for directories of Zoteroing output that do not downloaded
        files in them
            that is, the Zoteroing process couldn't fetch research-work related
            files during its process
        then flag all those URLs for manual processing as well
        '''
        res = []

        p2c = self._info_json_paths_and_content(pth)
        for (path, content) in p2c.items():
            url = content['URL']

            if content['error']:
                res.append(url)

        seen_urls = set(res)

        u2fb = self._get_bibtex_and_files(pth)
        for (url, fb) in u2fb.items():
            if url in seen_urls:
                continue

            if u2fb[url] is None:
                res.append(url)
                continue

            if not "files" in u2fb[url]:
                res.append(url)
                continue

            if len(u2fb[url]["files"]) == 0:
                res.append(url)
                continue

        return res

    def manual_handling_file(self, _name="needs_manual_handling.html"):
        return self._manual_handling_file(self._output_path, _name)

    def _manual_handling_file(self, pth, _name="needs_manual_handling.html"):
        '''
        Write or update a file containing the URLs that need manual handling
        '''

        from pathlib import Path
        file = Path(pth) / _name

        res = []
        if file.exists():
            import pandas as pd
            for _df in pd.read_html(file):
                res.extend(_df["URL"].to_list())

        res.extend( self._URLs_need_manual_handling( pth ) )

        import pandas as pd
        df_html = pd.DataFrame()
        #then writeout only the unique URLs
        df_html["URL"] = list(set(res))

        df_html.style.hide_index()
        df_html.to_html(file, render_links=True)

        return df_html

    def assemble_zoteroing_output(self, _target_dir="results"):
        return self._assemble_zoteroing_output(self._output_path, _target_dir)

    def _assemble_zoteroing_output(self, pth, _target_dir="results"):
        '''
        Gather all of the files, bibtex, and URL information
        into single easy to work with folders
            The function automatically creates a "results" folder under pth
        '''

        from pathlib import Path
        results = Path(pth) / _target_dir

        if not results.exists():
            results.mkdir()

        #gather all the finished URLs, files, and bibtex information from
        #the output dir
        u2fb = self._get_bibtex_and_files(pth)
        urls = list(u2fb.keys())
        files_and_bibtex = [u2fb[u] for u in urls]

        res = {}
        for i in range(len(urls)):
            #number each output folder in the results dir
            _working = results / str( (i+1) )
            _working.mkdir()

            #gather all the information about URLs, files, and bibtexes
            url = urls[i]
            _fab = files_and_bibtex[i]
            bibtex = None
            if (not _fab is None) and ("bibtex" in _fab):
                bibtex = _fab["bibtex"]
            files = None
            if (not _fab is None) and ("files" in _fab):
                if (not _fab["files"] is None) and len(_fab["files"]) > 0:
                    files = _fab["files"]

            #writeout a file that has the URL in it
            url_file = _working / "url.txt"
            url_file.touch()
            url_file.write_text( url )

            res[url] = None

            #writeout the bibtex to a fil
            bib_file = _working / "bibtex.bib"
            if not bibtex is None:
                bib_file.touch()
                bib_file.write_text( bibtex )

                if res[url] is None:
                    res[url] = {}
                res[url]["bibtex"] = str(bib_file.resolve())

            #and copy all the files from the output to the results folder
            #making sure to sanitize their file names to avoid copying issues
            #or strange file systems issues as a result of invalid filenames
            if not files is None:
                if res[url] is None:
                    res[url] = {}
                res[url]["files"] = []

                for f in files:
                    from pathlib import Path
                    _f = Path(f)

                    _src = str(_f)

                    from pathvalidate import sanitize_filename
                    _dst = _working / sanitize_filename( _f.name )
                    _dst = _dst.resolve()
                    _dst = str( _dst )

                    import shutil
                    shutil.copyfile(_src, _dst)

                    res[url]["files"].append( _dst )
        return res