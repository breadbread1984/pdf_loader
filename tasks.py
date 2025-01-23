#!/usr/bin/python3

import uuid
from os.path import join, exists, splitext, basename
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import wget

def download(input_args):
  url, output_path, description, retry = input_args
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

from minio import Minio
from minio.error import S3Error

def minio_upload(input_args):
  minio_host, minio_user, minio_password, minio_bucket, file_path, description = input_args
  client = Minio(
    endpoint = minio_host,
    access_key = minio_user,
    secret_key = minio_password,
    secure = False
  )
  try:
    found = client.bucket_exists(minio_bucket)
    if not found:
      client.make_bucket(minio_bucket)
    client.fput_object(
      minio_bucket
      basename(file_path)
      file_path
    )
  except S3Error as exc:
    return {'file_path': file_path, 'url': None, 'description': description}
  return {'file_path': file_path, 'url': f'{minio_host}/{minio_bucket}/{basename(file_path)}', 'description': description}
