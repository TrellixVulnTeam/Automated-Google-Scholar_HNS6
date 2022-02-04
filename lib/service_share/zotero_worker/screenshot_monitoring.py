'''
Take screenshots during execution so that progress on the Zoteroing can be
monitored
    One thing to check for is rare errors where the Zoteroing gets stuck
    waiting for Zotero to open, when the screenshots don't match
'''

from pathlib import Path
output_dir = Path("/home/headless/tmp")
screenshot_delay = 10

while True:
    #this returns in the format: 2021-12-27T01:24:25.772104_000
    #but the colons make this an invalid file name, so convert to periods
    from datetime import datetime
    timestamp = str(datetime.now().isoformat())
    timestamp = timestamp.replace(":", ".")
    
    #supply an extension so that save() knows what format to use
    filename = timestamp + ".png"

    save_path = output_dir / filename

    import pyautogui
    screenshot = pyautogui.screenshot()

    screenshot.save(save_path)

    import time
    time.sleep(screenshot_delay)