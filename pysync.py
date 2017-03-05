#!/usr/bin/env python3
import glob
import subprocess
from threading import Thread
import argparse
from progress.bar import Bar
from queue import Queue
import logging

__author__ = 'j4hangir'

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def _progress_thread(q: Queue, total: int):
  bar = Bar('Prcocessing', max=total)
  bar.next(0)
  while True:
    i = q.get()
    bar.next(i)
    q.task_done()


def _scp_thread(q: Queue, pq: Queue, rpath):
  while True:
    path = q.get()
    subprocess.Popen(["rsync", "-roR", path, rpath]).communicate()
    q.task_done()
    pq.put(1)


def main():
  parser = argparse.ArgumentParser(description="Python rsync threader")
  parser.add_argument("path", help="Glob path to recursively upload", type=str)
  parser.add_argument("rpath", help="rpath, i.e. user@host:path", type=str)
  parser.add_argument("-t", help="Threads number", default=4, type=int)
  args = parser.parse_args()
  
  logger.info("Scanning files")
  files = list(glob.iglob(args.path, recursive=True))
  
  queue, pqueue = Queue(), Queue()
  
  Thread(target=_progress_thread, args=(pqueue, len(files)), daemon=True).start()
  for i in range(args.t):
    Thread(target=_scp_thread, args=(queue, pqueue, args.rpath), daemon=True).start()
  
  for fp in files:
    queue.put_nowait(fp)
  try:
    queue.join()
  except KeyboardInterrupt:
    pass


if __name__ == '__main__':
  main()
