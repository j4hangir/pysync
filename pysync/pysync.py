#!/usr/bin/env python3
__author__ = 'j4hangir'
__all__ = ['main']

import glob
import subprocess
from threading import Thread
import argparse
from queue import Queue
from tqdm import tqdm
from loguru import logger


def progress_thread(q: Queue, total: int):
    with tqdm(total=total) as bar:
        while True:
            i = q.get()
            bar.update(i)
            q.task_done()


def scp_thread(q: Queue, pq: Queue, rpath):
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
    
    Thread(target=progress_thread, args=(pqueue, len(files)), daemon=True).start()
    for i in range(args.t):
        Thread(target=scp_thread, args=(queue, pqueue, args.rpath), daemon=True).start()
    
    for fp in files:
        queue.put_nowait(fp)
    try:
        queue.join()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
