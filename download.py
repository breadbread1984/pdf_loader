#!/usr/bin/python3

from absl import flags, app
from shutil import rmtree
from os import mkdir, remove
from os.path import exists
import json
import concurrent.futures
import psycopg2
from tasks import download, minio_upload

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('input_json', default = 'pdf_list.json', help = 'a list of pdf')
  flags.DEFINE_string('download_path', default = 'pdfs', help = 'path to directory')
  flags.DEFINE_string('minio_host', default = 'localhost:9000', help = 'minio host')
  flags.DEFINE_string('minio_user', default = 'minioadmin', help = 'minio username')
  flags.DEFINE_string('minio_password', default = 'minioadmin', help = 'minio password')
  flags.DEFINE_string('minio_bucket', default = 'references', help = 'minio bucket')
  flags.DEFINE_string('psql_host', default = 'localhost', help = 'postgresql host')
  flags.DEFINE_string('psql_port', default = '5432', help = 'postgresql port')
  flags.DEFINE_string('psql_user', default = 'igs', help = 'postgresql username')
  flags.DEFINE_string('psql_db', default = 'igs', help = 'postgresql database')
  flags.DEFINE_string('psql_password', default = 'igs', help = 'postgresql password')
  flags.DEFINE_integer('retry', default = 5, help = 'retry times')
  flags.DEFINE_integer('workers', default = 32, help = 'number of workers')
  flags.DEFINE_boolean('new', default = False, help = 'whether the download task is new')

def main(unused_argv):
  # download all pdfs
  with open(FLAGS.input_json, 'r') as f:
    pdfs = json.loads(f.read())
  if FLAGS.new:
    if exists(FLAGS.download_path): rmtree(FLAGS.download_path)
    mkdir(FLAGS.download_path)
    remove('download_succeed.json')
    remove('minio_succeed.json')
  if not exists('download_succeed.json'):
    download_tasks = list()
    for description, pdf_list in pdfs.items():
      for _, url in pdf_list.items():
        download_tasks.append((url, FLAGS.download_path, description, FLAGS.retry))
    with concurrent.futures.ThreadPoolExecutor(max_workers = FLAGS.workers) as executor:
      results = list(executor.map(download, download_tasks))
    failed_results = list(filter(lambda x: x['output_path'] is None, results))
    succeed_results = list(filter(lambda x: x['output_path'] is not None, results))
    with open('download_failed.json', 'w') as f:
      f.write(json.dumps(failed_results))
    with open('download_succeed.json', 'w') as f:
      f.write(json.dumps(succeed_results))
  else:
    with open('download_succeed.json', 'r') as f:
      succeed_results = json.loads(f.read())
  # add to object storing serivce
  if not exists('minio_succeed.json'):
    minio_tasks = list()
    for file_detail in succeed_results:
      minio_tasks.append((
        FLAGS.minio_host,
        FLAGS.minio_user,
        FLAGS.minio_password,
        FLAGS.minio_bucket,
        file_detail['output_path'],
        file_detail['url'],
        file_detail['filename'],
        file_detail['description']
      ))
    with concurrent.futures.ThreadPoolExecutor(max_workers = FLAGS.workers) as executor:
      results = list(executor.map(minio_upload, minio_tasks))
    failed_results = list(filter(lambda x: x['minio_url'] is None, results))
    succeed_results = list(filter(lambda x: x['minio_url'] is not None, results))
    with open('minio_failed.json', 'w') as f:
      f.write(json.dumps(failed_results))
    with open('minio_succeed.json', 'w') as f:
      f.write(json.dumps(succeed_results))
  else:
    with open('minio_succeed.json', 'r') as f:
      succeed_results = json.loads(f.read())
  # add to sql database
  conn = psycopg2.connect(
    database = FLAGS.psql_db,
    user = FLAGS.psql_user,
    password = FLAGS.psql_password,
    host = FLAGS.psql_host,
    port = FLAGS.psql_port,
  )
  cur = conn.cursor()
  for detail in succeed_results:
    url = detail['url']
    filename = detail['filename']
    description = detail['description']
    object_url = detail['minio_url']
    cur.execute(f"insert into materials (url, filename, description, object_url) values ('{url}','{filename}','{description}','{object_url}')")
    conn.commit()

if __name__ == "__main__":
  add_options()
  app.run(main)

