#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import concurrent.futures
import time
import os
import random


def worker(sleep_time=10) -> str:
    """ echo process id and sleep for 10 seconds """
    pid = os.getpid()
    print(f"Process {pid} started, sleep for {sleep_time} seconds")
    time.sleep(10)
    print(f"Process {pid} finished")
    return f"Process {pid} finished"


def main():
    num_process = os.cpu_count() - 2
    futures = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_process) as executor:
        for i in range(num_process):
            futures.append(executor.submit(worker, random.randint(5, 10)))
    print(f"All processes submitted, got {len(futures)} futures")

    for future in concurrent.futures.as_completed(futures):
        print(future.result())


if __name__ == '__main__':
    pid = os.getpid()
    print(f"Main process {pid} started")
    main()
    print(f"Main process {pid} finished")
