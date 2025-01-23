#!/usr/bin/python3

from absl import flags, app
from shutil import rmtree
from os import mkdir
import json
import minio
import concurrent.futures
from tasks import download

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('input_json', default = 'pdf_list.json', help = 'a list of pdf')
  flags.DEFINE_string('download_path', default = 'pdfs', help = 'path to directory')
  flags.DEFINE_integer('retry', default = 5, help = 'retry times')
  flags.DEFINE_integer('workers', default = 16, help = 'number of workers')

def main(unused_argv):
  # download all pdfs
  if exists(FLAGS.download_path): rmtree(FLAGS.download_path)
  mkdir(FLAGS.download_path)
  with open(FLAGS.input_json, 'r') as f:
    pdfs = json.loads(f.read())
  download_tasks = list()
  for description, pdf_list in pdfs.items():
    for _, url in pdf_list:
      download_tasks.append((url, FLAGS.download_path, description, FLAGS.retry))
  with concurrent.futures.ThreadPoolExecutor(max_workers = FLAGS.workers) as executor:
    results = list(executor.map(download, download_tasks))
  # add to object storing serivce
