import multiprocessing
import os
import numpy as np
from simhash import SimHash
import file_getter
from filelock import FileLock
import jsonlines
import pandas as pd
import time


def rehash(file):
   
    

def convert_to_npy(file):
    fsize = os.path.getsize(file)
    

def init_worker(dirs):
    save_fp = './index_vecs/64_robust_float32_query/'
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    indexes = np.load(selected_hash_fp)[16:32,:]
    hasher = SimHash(indexes)

    #read all the directories and find files that need to be split up or converted
    for chunk in dirs:
        match_16 = os.listdir(save_fp + chunk + '/')
        for full_match in match_16:
                      
    print(dirs)

def main():

    # Number of worker processes (adjust as needed)
    num_processes = multiprocessing.cpu_count()
    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=num_processes) 
    save_fp = './index_vecs/64_robust_float32_query/'
    match_8 = os.listdir(save_fp)
    match_8.sort()
    chunk_size = int(len(match_8) / num_processes)
    chunk_dirs = []
    while match_8:
        chunk_dirs.append(match_8[:chunk_size])
        match_8 = match_8[chunk_size:]
    # Start reading files concurrently
    for chunk_dir in chunk_dirs:
        print('starting: ', len(chunk_dir))
        #pool.apply_async(init_workers, args=(chunk_dir))

    #pool.close()
    #pool.join()



if __name__ == "__main__":
    main()
    #query_run(50302, 51302, '7tvuLLroI0n6uYBWuFig5d')
