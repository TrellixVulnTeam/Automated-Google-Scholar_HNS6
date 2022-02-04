import logging
LOG = logging.getLogger(__name__)

_proc_name = 'zotero-bin'
_zotero_UI_screenshot = "/home/headless/bin/zotero_clean.png"
_export_path = '/home/headless/tmp/My Library'

def start(): return _start()

def _start():
    '''
    Waiting for Zotero to open
    then returning its process handler

    while redirecting its logging to a file
    '''
    #close any open Zotero's
    _close()

    _launch_process()

    #then waiting for the Zotero UI to open
    LOG.debug("Waiting for Zotero UI to appear")

    import _util as util
    return util.wait_for( _is_UI_up )

def _focus():
    if _is_running():
        return _launch_process()
    else:
        return _start()

def _launch_process():
    LOG.debug("Opening Zotero")
    #then open a new one
    import subprocess
    subprocess.Popen(["zotero"])

    #waiting for the Zotero process to open
    import _util as util
    if not util.waiting_for_process( _proc_name ):
        LOG.debug("Could not see Zotero process appear")
        return False
    return True

def close():
    return _close()

def _close():
    LOG.debug("Closing Zotero.")
    
    import _util as util
    return util.close_process( _proc_name )

def is_running(): return _is_running()

def _is_running():
    LOG.debug("Checking if Zotero is running")

    import _util as util
    return util.is_process_live(_proc_name)

def is_UI_up():
    return _is_zotero_UI_up()

def _is_UI_up():
    LOG.debug("Checking if Zotero UI visible and ready")

    from PIL import Image
    import imagehash
    reference_image = Image.open( _zotero_UI_screenshot )
    hash_reference_image = imagehash.phash(reference_image)

    import tempfile
    with tempfile.NamedTemporaryFile() as fp:
        #create a screenshot of the desktop, to see if the Zotero UI has appeared
        #(saving the screenshot in a temp directory)
        import subprocess
        subprocess.run(["xfce4-screenshooter", "--delay", "1", "--window", "--save", fp.name])

        #then given this new screenshot, compare it with our reference screenshot to see if have a match
        from PIL import Image
        latest_image = Image.open( fp.name )

        #check if images are different
        #see:
        #https://pypi.org/project/ImageHash/
        #https://stackoverflow.com/questions/52736154/how-to-check-similarity-of-two-images-that-have-different-pixelization
        #https://stackoverflow.com/questions/35176639/compare-images-python-pil
        #https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.getbbox
        #https://pillow.readthedocs.io/en/stable/reference/ImageChops.html
        #https://stackoverflow.com/questions/20580785/python-how-to-detect-any-changes-in-the-screen

        #here we take the PERCEPTUAL HASH of the two images
        #phash performs well for these types of hashes: https://content-blockchain.org/research/testing-different-image-hash-functions/
        #then compare them
        #from testing small difference seem to be 10 or lower, while large differences are 30 or higher

        import imagehash
        hash_latest_image = imagehash.phash(latest_image)

    if abs(hash_reference_image - hash_latest_image) < 12:
        LOG.debug("Zotero UI is ready")
        return True

    LOG.debug("Could not find Zotero UI")
    return False

class Previous_export_found(Exception): pass
class Zotero_not_ready(Exception): pass
class Export_dialog_error(Exception): pass
class Export_save_dialog_error(Exception): pass
class Export_files_do_not_exist(Exception): pass

def export():
    #if there's already a "My Library" in the home directory, then exit with
    #error, we shouldn't see one of those when exporting
    from pathlib import Path
    if Path(_export_path).exists():
        raise Previous_export_found()

    #focus Zotero, so we can send it commands
    if not _focus():
        LOG.debug("Could not work with Zotero for export")
        raise Zotero_not_ready()

    #then opening the file menu
    import pyautogui
    pyautogui.hotkey('alt', 'f')

    #then up twice to get to the "export" option
    import pyautogui
    pyautogui.press(['up', 'up'])

    #then enter to start the export process
    import pyautogui
    pyautogui.press(['enter'])

    import _util as util
    timer = util.Timer(60*3)

    #then waiting for the "export" dialog to appear (this can take some time)
    while True:
        #make sure we can see multiple parts of the dialog
        #to confirm it's onscreen, since pyautogui's image detection
        #can be quite poor
        from pathlib import Path
        import pyautogui
        pth_pic1 = Path("/home/headless/bin/") / "export_logo.png"
        res1 = pyautogui.locateCenterOnScreen(str(pth_pic1), confidence=.9)

        from pathlib import Path
        import pyautogui
        pth_pic2 = Path("/home/headless/bin/") / "export_character_encoding.png"
        res2 = pyautogui.locateCenterOnScreen(str(pth_pic2), confidence=.9)

        from pathlib import Path
        import pyautogui
        pth_pic3 = Path("/home/headless/bin/") / "export_format_word.png"
        res3 = pyautogui.locateCenterOnScreen(str(pth_pic3), confidence=.9)

        from pathlib import Path
        import pyautogui
        pth_pic4 = Path("/home/headless/bin/") / "export_translator_options.png"
        res4 = pyautogui.locateCenterOnScreen(str(pth_pic4), confidence=.9)

        from pathlib import Path
        import pyautogui
        pth_pic5 = Path("/home/headless/bin/") / "export_zotero_logo_and_export.png"
        res5 = pyautogui.locateCenterOnScreen(str(pth_pic5), confidence=.9)

        if sum([1 for r in [res1, res2, res3, res4, res5] if r is not None]) >= 4:
            break

        import time
        time.sleep(1)

        if timer.timed_out():
            raise Export_dialog_error()

    LOG.debug("Exporting the Zotero library.")

    #then hit the "okay" button on the export dialog
    #since the options for what type of export should already be set
    import pyautogui
    pyautogui.hotkey('enter')

    #wait for the save dialog to appear
    '''
    Note that pyautogui fails to detect
    the save dialog here
    so we use the workaround of trying to
    copy text
    this is because when the save dialog appears
    some text is highlighted, allowing us to
    copy it, indicating that the save dialog
    has appeared
    '''

    import _util as util
    timer = util.Timer(60*2)

    while True:
        #copy whatever is selected
        import pyautogui
        pyautogui.hotkey('ctrl', 'c')

        #check the clipboard
        import _util as util
        if len( util.get_clipboard() ) > 0:
            break
        
        import time
        time.sleep(1)

        if timer.timed_out():
            raise Export_save_dialog_error()

    LOG.debug(f"Saving exported Zotero library to: {_export_path}")

    #since we have the portion of the export dialog highlighted that prompts
    #for a save path, then attempt to save the export in the 'tmp' directory
    import pyautogui
    pyautogui.typewrite(_export_path)

    #then click the save button
    pyautogui.click(1283, 737, clicks=1, button='left')

    #when waiting for the export to complete
    import _util as util
    timer = util.Timer(60*2)

    while True:
        from pathlib import Path
        if Path(_export_path).exists():
            break

        if timer.timed_out():
            raise Export_files_do_not_exist()

        import time
        time.sleep(1)

    LOG.debug(f"Saw exported library at: {_export_path}")

    library_bib = Path( _export_path ) / "My Library.bib"
    #then read the bibtext exported
    
    #use custom parser for so-called "common strings"
    #output by Zotero
    #see: https://github.com/sciunto-org/python-bibtexparser/issues/204
    with open(library_bib, "r", encoding='utf-8') as bibtex_file:
        import bibtexparser
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        bib_database = bibtexparser.load( bibtex_file, parser=parser)

    LOG.debug("Parsed from Zotero database:")
    import json

    LOG.debug( "\n" )
    LOG.debug( json.dumps(bib_database.get_entry_dict(), sort_keys=True, indent=4) )
    LOG.debug( "\n" )

    if len(bib_database.entries) > 0:
        LOG.debug(f"Saw at least one reference in the library.")
        return bib_database.entries
    else:
        LOG.debug(f"Didn't see any references.")
        return {}

def get_export_entry_types(_l):
    '''
    we use bibtexparser for parsing the bibtex that comes out of Zotero
    These entries contain a key "ENTRYTYPE", which shows what type of
    information is assocaited with each bibtext entry
        where each entry maps to information about one research-work in the Zotero
        library
    Thus, given an entry list from bibtexparser, return the name and number of
    "ENTRYTYPE" keys in the list
    '''

    if len(_l) == 0:
        return {}

    _ret = {}
    for _itm in _l:
        if "ENTRYTYPE" in _itm:
            if not _itm["ENTRYTYPE"] in _ret:
                _ret[_itm["ENTRYTYPE"]] = 0
            
            _ret[_itm["ENTRYTYPE"]] += 1

    return _ret

def cleanup_export():
    from pathlib import Path
    if Path(_export_path).exists():
        import shutil
        shutil.rmtree(Path(_export_path), ignore_errors=True)

def get_path_to_export():
    from pathlib import Path
    if Path(_export_path).exists():
        return str(_export_path)
    return None