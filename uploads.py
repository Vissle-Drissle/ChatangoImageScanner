import re
import math
import time
import asyncio
from yarl import URL
from pathlib import Path
from aiohttp import ClientSession

DOWNLOAD = True

"""
A script to display uploaded images from a user and download them.

Version: 1.0.0
Author: @Cheese [https://github.com/Vissle-Drissle]
Requirements:
  - Python ^3.10.x
  - yarl
  - aiohttp[speedups]
"""

class Uploads:
  def __init__(self, directory: str="img"):
    self.cache = {}
    self.headers = {
      "Accept-Encoding": "gzip, deflate, br, zstd",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://st.chatango.com/",
      "Sec-Fetch-Dest": "image",
      "Sec-Fetch-Mode": "no-cors",
      "Sec-Fetch-Site": "same-site",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
      "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "accept-language": "en-US,en;q=0.9",
      }
    self.hosts = {
      "ust.chatango.com": "st.chatango.com",
      "st.chatango.com": "ust.chatango.com"
      }
    self.host = "ust.chatango.com"
    self.probed = 0
    self.directory = Path(directory)

  # Convert image size bytes to KB/MB
  def image_size(self, byte: int):
    if byte < 1024:
      return f"{byte} B"
    elif byte < 1024 ** 2:
      return f"{byte / 1024:.2f} KB"
    else:
      return f"{byte / (1024 ** 2):.2f} MB"

  # Check image thumbnail or content (when downloading) if it exists
  async def fetch(self, session, url, timeout: int=None, download: bool=False):
    if download:
      url = url.replace("t_", "l_", 1)

    async with session.request(method=download and "GET" or "HEAD", url=url, headers=self.headers, timeout=timeout) as response:
      if response.status == 200:
        headers = response.headers
        if download:
          link = URL(url)
          image = await response.read()
          (self.directory / link.parts[4]).mkdir(parents=True, exist_ok=True)
          filename = link.parts[-1]
          fp = self.directory / link.parts[4] / filename
          with open(fp, "wb") as file:
            file.write(image)

        return {"link": url.replace("t_", "l_", 1), "date": headers.get("Last-Modified"), "size": int(headers.get("Content-Length"))}

  async def fetch_all(self, session, urls, download: bool=False):
    tasks = [self.fetch(session, url, download=download) for url in urls]
    result = await asyncio.gather(*tasks)
    return [response for response in result if response]

  # Fetch and return the first image URL that was found
  async def fetch_first(self, session, urls):
    tasks = [asyncio.create_task(self.fetch(session, url)) for url in urls]
    try:
      for task in asyncio.as_completed(tasks):
        response = await task
        if response is not None:
          for t in tasks:
            if not t.done():
              t.cancel()
          await asyncio.gather(*tasks, return_exceptions=True)
          return response
    finally:
      for t in tasks:
        if not t.done():
          t.cancel()
      await asyncio.gather(*tasks, return_exceptions=True)
    return None

  # In the event that ust/st is unavaialble/ratelimited
  async def probe(self, session):
    try:
      if self.probed < time.time():
        self.probed = time.time() + 300
        await self.fetch(session, f"https://{self.host}", timeout=5)
    except Exception as e:
      self.host = self.hosts.get(self.host, "st.chatango.com")

  # I have yet to see an account with more than 100,000 uploads, so it is hard-coded for now
  async def search(self, user: str, start: int=0, stop: int=100_000, download: bool=False):
    ts = time.time()
    try:
      if start < 0 or stop > 100_000:
        return {"error": "Start or stop are out of range", "images": []}

      # If valid username
      if not re.match("^([a-zA-Z0-9]{1,20})$", user):
        return {"images": [], "time": time.time() - ts}

      user = user.lower()
      async with ClientSession(headers=self.headers) as session:
        await self.probe(session)
        if user in self.cache:
          start = math.floor(self.cache[user] / 20) * 20
          del self.cache[user]

        path = f"{user[0]}/{user[1] if len(user) > 1 else user[0]}/{user}"
        urls = [f"https://{self.host}/um/{path}/img/t_{x}.jpg" for x in range(start, stop, 20)]
        url = await self.fetch_first(session, urls)
        if url:
          hit = url["link"].split("l_")[1].split(".")[0]
          amount = int(hit)
          all_urls = [f"https://{self.host}/um/{path}/img/t_{x}.jpg" for x in range(max(0, amount - 20), amount + 20)]
          check = await self.fetch_all(session, all_urls, download=download)
          numbers = [int(x["link"].split("l_")[1].split(".")[0]) for x in check]
          self.cache[user] = min(numbers)
          return {"images": check, "time": time.time() - ts}

        return {"images": [], "time": time.time() - ts}
    except Exception as e:
      print(e)
      return {"images": [], "time": time.time() - ts}

get_uploads = Uploads()

while True:
  target = input("Username: ")
  query = get_uploads.search(target, download=DOWNLOAD)
  search = asyncio.run(query)

  display = [f'[{x["date"]}] {x["link"]} ({get_uploads.image_size(x["size"])})' for x in search["images"]]
  images = "\n".join(display)
  print(images)
  print(f'Time taken: {search["time"]:.2f}s, total images: {len(search["images"])}\n')
