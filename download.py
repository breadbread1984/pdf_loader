#!/usr/bin/python3

from absl import flags, app
from shutil import rmtree
from os import mkdir
import json
import concurrent.futures
from tasks import download, minio_upload

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('input_json', default = 'pdf_list.json', help = 'a list of pdf')
  flags.DEFINE_string('download_path', default = 'pdfs', help = 'path to directory')
  flags.DEFINE_string('minio_host', default = 'http://localhost:9000', help = 'minio host')
  flags.DEFINE_string('minio_user', default = 'minioadmin', help = 'minio username')
  flags.DEFINE_string('minio_password', default = 'minioadmin', help = 'minio password')
  flags.DEFINE_string('minio_bucket', default = 'references', help = 'minio bucket')
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
  failed_results = list(filter(lambda x: x['output_path'] is None, results))
  succeed_results = list(filter(lambda x: x['output_path'] is not None, results))
  with open('download_failed.json', 'w') as f:
    f.write(json.dumps(failed_results))
  # add to object storing serivce
  minio_tasks = list()
  for file_detail in succeed_results:
    minio_tasks.append((
      FLAGS.minio_host,
      FLAGS.minio_user,
      FLAGS.minio_password,
      FLAGS.minio_bucket,
      file_detail['output_path'],
      file_detail['description']
    ))
  with concurrent.futures.ThreadPoolExecutor(max_workers = FLAGS.workers) as executor:
    results = list(executor.map(minio_upload, minio_tasks))
  failed_results = list(filter(lambda x: x['url'] is None, results))
  succeed_results = list(filter(lambda x: x['url'] is not None, results))
  with open('minio_failed.json', 'w') as f:
    f.write(json.dumps(failed_results))
  # add to sql database

if __name__ == "__main__":
  add_options()
  app.run(main)

