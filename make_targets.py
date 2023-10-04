import multiprocessing
import os
import file_getter
import numpy as np
from simhash import SimHash
import random

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
                print('make dir: ', target_dir)
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
    try:
        selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
        fg = file_getter.FileGetter(chunk_start+1, chunk_end)
        #MAGIC NUMBERS ARE BAD BUT HERE ARE SOME THAT CONTROL THE SELECTED VECTORS FOR COSINE SIMILARITY
        indexes = np.load(selected_hash_fp)[0:16,:]
        hasher = SimHash(indexes)
        uid = None
        while not(fg.exhausted_dirs):
            #print(fg.dirs_len - fg.dir_idx)
            uid = fg.get_uid()
            print('chunk_start: ', chunk_start, ' processing:', uid)
            #for x in range(1):
            for idx, seg in enumerate(fg.segs):
                byte, hex_dirs = hasher.hash(seg)
                #print('saving byte: ', idx)
                try:
                    lock.acquire()
                    save_byte(idx, uid, byte, hex_dirs)
                    lock.release()
                except Exception as e:
                    print(e)
            fg.get_next_file()
        return uid
    except Exception as e:
        return e

"""
This was needed because I didn't save the latest cursor location when making indexes originally.
"""
def get_cursor_location(lock, chunk_start, chunk_end):
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    fg = file_getter.FileGetter(chunk_start, chunk_end)
    #fg.ordered_dirs has all the possible latest dirs
    #dir_range = np.array(fg.ordered_dirs, dtype = np.unicode_)
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
                lock.acquire()
                arr = np.load(save_fp + match_dir + '/' + full_match + '/matches.npy')
                lock.release()
                uid_arr = arr['uid']
                uid_arr = np.char.encode(uid_arr, 'utf-8')
                uid_arr = np.char.decode(uid_arr, 'utf-8')
                #print(uid_arr.shape)
                for uid in np.ndarray.tolist(uid_arr):
                    #print(uid.dtype)
                    #print()
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
                print(e)
                #print(match_dir, '/', full_match)
    print('[',chunk_start,':',chunk_end,'] latest dir_idx: ',latest_dir_idx,'- at dir -', dir_range[latest_dir_idx])
    #with 'last_cursor.txt' as 

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
    #latest_cursors = []
    # Start reading files concurrently
    for (start_idx, chunk_len) in zip(start_idxs, chunk_lens):
        pool.apply_async(init_workers, args=(lock,start_idx, start_idx+chunk_len))
        #print(ret.get())
        #latest_cursors.append(last_uid)
        #pool.apply_async(get_cursor_location, args=(lock,start_idx, start_idx+chunk_len))
    pool.close()
    pool.join()
    #print(latest_cursors)
    # Close the pool and wait for all processes to complete
    #pool.close()
    #pool.join()
if __name__ == "__main__":
    main()
