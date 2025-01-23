#!/usr/bin/python3

import uuid
from os.path import join, exists, splitext
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import wget

def download(url, output_path, description, retry = 5):
  parsed_url = urlparse(url)
  original_fname = parsed_url.path.split('/')[-1]
  stem, ext = splitext(original_fname)
  renamed_fname = str(uuid.uuid4())
  if ext in ['.html', '.htm'] or not bool(urlparse(url).query):
    # html or pdf
    for i in range(retry):
      try:
        wget.download(url, out = join(output_path, renamed_fname))
      except:
        continue
  else:
    # javascript
    with sync_playwright() as p:
      browswer = p.chromium.launch()
      page = browser.new_page()
      for i in range(retry):
        try:
          page.goto(url)
          with page.expect_download() as download_info:
            download = download_info.value
          download.save_as(join(output_path, renamed_fname))
        except:
          continue
        if exists(join(output_path, original_fname)): break
      page.close()
  succeed = exists(join(output_path, renamed_fname))
  return {'url': url, 'filename': original_name, 'output_path': join(output_path, renamed_fname) if succeed else None, 'description': description}
