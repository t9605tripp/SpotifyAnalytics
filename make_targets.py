import multiprocessing
import os
import file_getter
import numpy as np
from simhash import SimHash

def save_byte(idx, uid, byte, hex_dirs):
    
    match_dt = np.dtype([('uid', np.unicode_, 22), ('sidx', np.uint16)])
    save_fp = './index_vecs/64_robust_float32_query/' 
    target_info = np.array([(uid, idx)], dtype=match_dt)
    save_dir = ''.join([x + '/' for x in hex_dirs])
    #print('saving byte to dir: ', uid, '  ', idx, '  ', save_dir)
    #print(save_dir)
    target_dir = save_fp + save_dir
    dir_exists = os.path.exists(target_dir)
    if not(dir_exists):
            try:
                #print('make dir: ', target_dir)
                os.makedirs(target_dir)
                np.save(target_dir + '/matches.npy', target_info)
            except Exception as e:
                return
    else:
        #print('saving to existing dir', target_dir)
        matches = np.load(target_dir + '/matches.npy')
        matches = np.append(matches, target_info)
        np.save(target_dir + '/matches.npy', matches)
    return

def init_workers(lock, chunk_start, chunk_end):
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    fg = file_getter.FileGetter(chunk_start, chunk_end)
    #MAGIC NUMBERS ARE BAD BUT HERE ARE SOME THAT CONTROL THE SELECTED VECTORS FOR COSINE SIMILARITY
    indexes = np.load(selected_hash_fp)[0:16,:]
    hasher = SimHash(indexes)
    while not(fg.exhausted_dirs):
        uid = fg.get_uid()
        print(uid)
        #for x in range(1):
        for idx, seg in enumerate(fg.segs):
            byte, hex_dirs = hasher.hash(seg)
            #print('saving byte: ', idx)
            lock.acquire()
            save_byte(idx, uid, byte, hex_dirs)
            lock.release()
        fg.get_next_file()
    return

def main():
    # Number of worker processes (adjust as needed)
    num_processes = multiprocessing.cpu_count()
    print(num_processes)
    # Create a multiprocessing manager and a queue to collect results
    #manager = multiprocessing.Manager()
    #result_queue = manager.Queue()

    # Create a pool of worker processes
    #lock = multiprocessing.Lock()
    pool = multiprocessing.Pool(processes=num_processes)
    manager = multiprocessing.Manager()
    lock = manager.Lock()
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
        pool.apply_async(init_workers, args=(lock,start_idx, start_idx+chunk_len))
    pool.close()
    pool.join()
    # Close the pool and wait for all processes to complete
    #pool.close()
    #pool.join()
if __name__ == "__main__":
    main()
