import multiprocessing
import os
import file_getter
import numpy as np
from simhash import SimHash
import traceback
from filelock import FileLock

def save_byte(idx, uid, byte, hex_dirs):
    match_dt = np.dtype([('uid', np.unicode_, 22), ('sidx', np.uint16)])
    save_fp = './index_vecs/64_robust_float32_query/' 
    target_info = np.array([(uid, idx)], dtype=match_dt)
    save_dir = ''.join([x + '/' for x in hex_dirs])
    #print('saving byte to dir: ', uid, '  ', idx, '  ', save_dir)
    #print(save_dir)
    target_dir = save_fp + save_dir
    dir_exists = os.path.exists(target_dir)
    lock = FileLock(f'{target_dir}.lock')
    if not(dir_exists):
            try:
                print('make dir: ', target_dir)
                os.makedirs(target_dir)
                lock.acquire()
                np.save(target_dir + '/matches.npy', target_info)
                lock.release()
            except Exception as e:
                traceback.print_exc()
    else: 
        #with lock:
        #    with open("high_ground.txt", "a") as f:
        #        f.write("You were the chosen one.")
        if not(os.path.exists(target_dir + '/matches.npy')):
            lock.acquire()
            #with lock:
            np.save(target_dir + '/matches.npy', target_info)
            lock.release()
        else:
        #print('saving to existing dir', target_dir)
            #lock.acquire()
            #with lock:
            lock.acquire()
            matches = np.load(target_dir + '/matches.npy', allow_pickle=True)
            #lock.release()
            matches = np.append(matches, target_info)
            #lock.acquire()
            np.save(target_dir + '/matches.npy', matches)
            lock.release()
    return

def init_workers(chunk_start, chunk_end, cursor):
    try:
        selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
        fg = file_getter.FileGetter(chunk_start, chunk_end, cursor)
        #MAGIC NUMBERS ARE BAD BUT HERE ARE SOME THAT CONTROL THE SELECTED VECTORS FOR COSINE SIMILARITY
        indexes = np.load(selected_hash_fp)[0:16,:]
        hasher = SimHash(indexes)
        uid = None
        try:
            while not(fg.exhausted_dirs):
                #print(fg.dirs_len - fg.dir_idx)
                uid = fg.get_uid()
                print('chunk_start: ', chunk_start, ' processing:', uid)
                #It would be much more efficient to operate on all the matrix at once then write it
                byte_data, hex_dirs = hasher.hash_all(fg.segs)
                """
                for idx, seg in enumerate(fg.segs):
                    byte, hex_dirs = hasher.hash(seg)
                    #print('saving byte: ', idx)
                    try:
                        #print(uid)
                        lock.acquire()
                        save_byte(idx, uid, byte, hex_dirs)
                        lock.release()
                    except Exception as e:
                        print(hex_dirs)
                        print(uid)
                        traceback.print_exc()
                """
                fg.get_next_file()
        except Exception as e:
            return fg.get_uid()

        return uid
        
    except Exception as e:
        traceback.print_exc()


def get_latest_cursors(max_procs):
    latest_files = os.listdir('./index_vecs/last_cursors/')[-max_procs:]
    uids = []
    for file in latest_files:
        with open(f'./index_vecs/last_cursors/{file}') as f:
            content = f.read()
            uids.append(content.replace('\n', ''))
    uids.sort()
    return uids[:max_procs]

def write_cursor(ret):
    latest_files = os.listdir('./index_vecs/last_cursors/')
    next_idx = len(latest_files)
    with open(f'./index_vecs/last_cursors/{next_idx}.txt', 'w') as f:
        f.write(str(ret))

def main():
    # Number of worker processes (adjust as needed)
    num_processes = multiprocessing.cpu_count()
    #num_hashers = num_processes-1
    #print(num_processes)
    # Create a multiprocessing manager and a queue to collect results
    #manager = multiprocessing.Manager()
    #result_queue = manager.Queue()
    cursors = get_latest_cursors(num_processes)
    print(cursors)
    # Create a pool of worker processes
    #lock = multiprocessing.Lock()
    pool = multiprocessing.Pool(processes=num_processes)
    manager = multiprocessing.Manager()
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
    #ret_lock = manager.Lock()
    for x in range(num_processes):
        lock = manager.Lock()
        locks.append(lock)
    # Start reading files concurrently
    for (start_idx, chunk_len, cursor) in zip(start_idxs, chunk_lens, cursors):
        ret = pool.apply_async(init_workers, args=(start_idx, start_idx+chunk_len, cursor))
    #ret_lock.acquire()
    #write_cursor(ret)
    #ret_lock.release()
    ret = ret.get()
    print(f'ret-{start_idx}-{ret}')

    pool.close()
    pool.join()
    # Close the pool and wait for all processes to complete
if __name__ == "__main__":
    main()
