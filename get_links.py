#!/usr/bin/python3

from absl import flags, app
from os.path import splitext
import requests
import string
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('url', default = None, help = 'url')
  flags.DEFINE_string('output', default = 'links.json', help = 'path for output json')

def generate_random_string(length):
  all_characters = string.ascii_letters + string.digits
  random_string = ''.join(random.choice(all_characters) for i in range(length))
  return random_string

def main(unused_argv):
  all_links = dict()
  try:
    response = requests.get(FLAGS.url)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    for link in links:
      url = urljoin(FLAGS.url, link.get("href"))
      text = link.get_text()
      parsed_url = urlparse(url)
      f = parsed_url.path.split('/')[-1]
      stem, ext = splitext(f)
      if ext != '.pdf': continue
      if text.strip() == '' or text.strip() in all_links:
        text += generate_random_string(10)
      all_links[text] = url
  except:
    print('failed to access given url!')
    raise
  with open(FLAGS.output, 'w') as f:
    f.write(json.dumps(all_links, indent = 2))

if __name__ == "__main__":
  add_options()
  app.run(main)
