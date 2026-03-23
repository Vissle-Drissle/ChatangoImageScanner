# Chatango Image Scanner in Python
Display a users uploaded images and download them

# Requirements and dependencies
- Python ^3.10.x
- yarl ^1.23.0
- aiohttp ^3.13.3

```bash
pip install -r requirements.txt
pip install yarl aiohttp[speedups]
```

# Step by step

1. Install [Python](https://www.python.org/) version 3.10+ and make sure `Add Python to PATH` and `pip` are checked
2. Open command prompt and type `pip install yarl aiohttp[speedups]`, if `pip is not recognized` check the above step by opening the Python installer and modifying the installation with pip, or restart your device.
3. Download the latest version of the scanner from [Releases](https://github.com/Vissle-Drissle/ChatangoImageScanner/releases) and extract files.
4. Run or double click `uploads.py` once all external dependencies have installed, if it closes immediately open it in Python IDE and run again to see errors.
5. Enter a username and retrieve results!

If you can't get it to work or are having other concerns, PM me on "[Cheese](https://cheese.chatango.com)" or send a message to [me](https://me.chatango.com).  
If this is too much or you can't be bothered, you may use the [online version](https://vissle.me/menu) instead.

# Some questions

- How are Chatango images stored?
> Chatango stores the last 20 images. When you upload an image, the oldest one is deleted.

- How does this work?
> The images are in a predictable URL format, the script goes through 0 to 100,000 of those URLs

- How do I remove images that are shown?
> You can upload the same image multiple times in your own group chat, this will delete the oldest

- How do I disable downloads?
> Edit uploads.py and at the top, change DOWNLOAD = True to DOWNLOAD = False