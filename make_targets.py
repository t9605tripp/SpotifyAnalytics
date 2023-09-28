import multiprocessing
import os
import file_getter
import numpy as np
from simhash import SimHash

def init_workers(chunk_start, chunk_end):
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    fg = file_getter.FileGetter(chunk_start, chunk_end)
    #MAGIC NUMBERS ARE BAD BUT HERE ARE SOME THAT CONTROL THE SELECTED VECTORS FOR COSINE SIMILARITY
    indexes = np.load(selected_hash_fp)[0:7,:]
    hasher = SimHash(indexes) 
    hasher.hash(fg.segs)
    

    #while not(fg.exhausted_dirs):
    #    fg.get_next_file()

    #print(fg.exhausted_dirs)
    #pid = os.getpid()
    #print(pid)
    #np.save(f'./logs/{max_segs}_timbre_data_{pid}',timbre_bounds)
    return
    # List to hold the results from each process
    #results = []
def main():
    # Number of worker processes (adjust as needed)
    num_processes = multiprocessing.cpu_count()

    # Create a multiprocessing manager and a queue to collect results
    #manager = multiprocessing.Manager()
    #result_queue = manager.Queue()

    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=num_processes)

    dirs = os.listdir('/home/tripptd/spotify/audio_analysis/')
    chunk_size = int(len(dirs) / num_processes)
    chunk_lens = []
    start_idxs = []
    start_idx = 0
    while dirs:
        start_idxs.append(start_idx)
        chunk_lens.append(len(dirs[:chunk_size]))
        start_idx += len(dirs[:chunk_size])
        dirs = dirs[chunk_size:]
    #There are 13 chunks
    #2495 dirs each chunk
    # Start reading files concurrently
    for (start_idx, chunk_len) in zip(start_idxs, chunk_lens):
        pool.apply_async(init_workers, args=(start_idx, start_idx+chunk_len))
    pool.close()
    pool.join()
    # Close the pool and wait for all processes to complete
    #pool.close()
    #pool.join()
if __name__ == "__main__":
    main()
