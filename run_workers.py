import multiprocessing
import os
import tqdm
import file_getter
import numpy as np
"""
idex_dt = np.dtype([('t1', np.float32), ('t2', np.float32),
        ('t3', np.float32), ('t4', np.float32), ('t5', np.float32), ('t6', np.float32),
        ('t7', np.float32), ('t8', np.float32), ('t9', np.float32), ('t10', np.float32),
        ('t11', np.float32), ('t12', np.float32), ('seg_start', np.float32),
        ('seg_dur', np.float32), ('seg_idx', np.float32)])
"""


def init_workers(chunk_start, chunk_end):
    fg = file_getter.FileGetter(chunk_start, chunk_end)
    #print(fg.curr_dir)
    print(fg.curr_file)
    #print(fg.get_random_timbre())
    #print(fg.curr_file)
    #max_segs = 100000
    #timbre_bounds = np.empty([max_segs,12],dtype=float32)
    #seg_ct = 0
    #while seg_ct < max_segs:
    #    timbre_bounds[seg_ct,] = get_timbre_bound_point()

if __name__ == "__main__":
    # List to hold the results from each process
    #results = []

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

    # Close the pool and wait for all processes to complete
    pool.close()
    pool.join()

    # Collect results from the queue
    #while not result_queue.empty():
    #    results.append(result_queue.get())

    # Combine the results from all processes as needed
    #combined_result = []
    #for result in results:
    #    combined_result.extend(result)

    # Process the combined result as needed
    # For example, you can analyze or manipulate the data in combined_result
    #print(combined_result)
    #print("Data from all files has been processed.")

