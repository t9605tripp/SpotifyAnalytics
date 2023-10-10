import multiprocessing
import os
import file_getter
import numpy as np
from simhash import SimHash
import random
from filelock import FileLock

#manager = multiprocessing.Manager()
#lock=manager.Lock()
"""
This was needed because I didn't save the latest cursor location when making indexes originally.
"""
def get_cursor_location(pnum, chunk_start, chunk_end):
    #global lock
    
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    fg = file_getter.FileGetter(chunk_start, chunk_end)
    dir_range = fg.ordered_dirs
    dir_range.sort()
    #print(dir_range)
    #While you haven't found the latest file location, read all the matches.
    save_fp = './index_vecs/64_robust_float32_query/'
    #First level of files
    match_8 = os.listdir(save_fp)
    random.shuffle(match_8)
    #Read through all the match files
    latest_dir_idx = 0
    latest_uid = None
    total = len(match_8)
    for m8_idx, match_dir in enumerate(match_8):
        #print('dirs left: ', total-m8_idx, 'latest_idx: ', latest_dir_idx, ' ', latest_uid)
        match_16 = os.listdir(save_fp + match_dir + '/')
        for full_match in match_16:
            try:
                lock = FileLock(f'./index_vecs/{full_match}.lock')
                lock.acquire()
                arr = np.load(save_fp + match_dir + '/' + full_match + '/matches.npy')
                lock.release()
                uid_arr = arr['uid']
                uid_arr = np.char.encode(uid_arr, 'utf-8')
                uid_arr = np.char.decode(uid_arr, 'utf-8')
                for uid in np.ndarray.tolist(uid_arr):
                    try:
                        dirname = uid[0:3]
                        #print(len(dir_range))
                        for midx, poss_match in enumerate(dir_range):
                            if poss_match == dirname:
                                #print(midx, ' - ', poss_match)
                        #dir_idx = dir_range.index(dirname)
                        #print(dir_idx, ' ', dirname)
                                if midx > latest_dir_idx:
                                    latest_dir_idx = midx        
                                    latest_uid = uid
                                    print('starting: ', chunk_start, ' - latest info: ',latest_dir_idx,' - ', uid, ' - ', dir_range[latest_dir_idx])
                    except ValueError as e:
                        pass
            except Exception as e:
                return e
                #print(match_dir, '/', full_match)
    #print('[',chunk_start,':',chunk_end,'] latest dir_idx: ',latest_dir_idx,'- at dir -', dir_range[latest_dir_idx])
    """with open(f'./index_vecs/{pid}.txt', 'w') as f:
        write_str = '[' + chunk_start + ':' + chunk_end + '] latest dir_idx: ' + latest_dir_idx + '- at dir -' + dir_range[latest_dir_idx]
        f.write(write_str)"""

def main():
    # Number of worker processes (adjust as needed)
    num_processes = multiprocessing.cpu_count()
    #print(num_processes)
    # Create a multiprocessing manager and a queue to collect results
    #manager = multiprocessing.Manager()
    #result_queue = manager.Queue()

    # Create a pool of worker processes
    #lock = multiprocessing.Lock()
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
    for pnum, (start_idx, chunk_len) in enumerate(zip(start_idxs, chunk_lens)):
        pool.apply_async(get_cursor_location, args=(pnum, start_idx, start_idx+chunk_len))

    pool.close()
    pool.join()
    #print(latest_cursors)
    # Close the pool and wait for all processes to complete
    #pool.close()
    #pool.join()
if __name__ == "__main__":
    main()
