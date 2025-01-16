#!/usr/bin/python3

from os import environ
from absl import flags, app
from shutil import rmtree
from os import mkdir, listdir
from os.path import join, exists, splitext
from langchain.document_loaders import UnstructuredPDFLoader

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('input_dir', default = 'samples', help = 'path to directory of pdf')
  flags.DEFINE_string('output_dir', default = 'output', help = 'path to output directory')

def main(unused_argv):
  if exists(FLAGS.output_dir): rmtree(FLAGS.output_dir)
  mkdir(FLAGS.output_dir)

  environ['OCR_AGENT'] = 'tesseract' # paddleocr

  for f in listdir(FLAGS.input_dir):
    stem, ext = splitext(f)
    if ext != '.pdf': continue
    loader = UnstructuredPDFLoader(join(FLAGS.input_dir, f), mode = 'single', strategy = 'hi_res', languages = ['en', 'zh-cn', 'zh-tw'])
    docs = loader.load()
    text = ' '.join([doc.page_content for doc in docs])
    with open(join(FLAGS.output_dir, f'{stem}.txt'), 'w') as out:
      out.write(text)

if __name__ == "__main__":
  add_options()
  app.run(main)
