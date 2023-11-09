import multiprocessing
import os
import file_getter
import numpy as np
from simhash import SimHash
import traceback
from filelock import FileLock
import jsonlines
import time
import shutil

def write_jsonl(fp, write_data): 
    #print(fp,'  ',(write_data))
    lock = FileLock(f'{fp}match.lock')
    with lock:
        #print("writing jsonl to", fp, '  ', write_data)
        with jsonlines.open(f'{fp}matches.jsonl', 'a') as f:
            f.write(write_data)
            #pass

def init_workers(chunk_start, chunk_end, cursor=None):
    try: 
        selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
        #print(chunk_start)
        cursor_actual = get_cursor(chunk_start, testing=True)
        #print('cursor_actual: ', chunk_start, ' | ', cursor_actual)
        fg = file_getter.FileGetter(chunk_start, chunk_end, cursor_actual)
        #MAGIC NUMBERS ARE BAD BUT HERE ARE SOME THAT CONTROL THE SELECTED VECTORS FOR COSINE SIMILARITY
        indexes = np.load(selected_hash_fp)[0:16,:]
        hasher = SimHash(indexes)
        uid = None
        try:
            #files_done = 2
            #while files_done > 0:
            while not(fg.exhausted_dirs):
                #start = time.time()
                uid = fg.get_uid()
                byte_data, hex_dirs = hasher.hash_all(fg.segs)
                
                with open(f'./index_vecs/last_cursors/_{chunk_start}_{cursor_actual}.txt', 'a') as f:
                    f.write(uid)
                    f.write('\n')
                if byte_data is not None:
                    try:
                        save_fp = './index_vecs/64_robust_float32_query/' 
                        for sidx, (byte, hex_dir) in enumerate(zip(byte_data, hex_dirs)):
                            save_dir = hex_dir[0] + '/' + hex_dir[1] + '/'
                            target_dir = save_fp + save_dir
                            dir_exists = os.path.exists(target_dir)
                            if not(dir_exists):
                                os.makedirs(target_dir)
                            write_jsonl(target_dir, [sidx, uid])
                    except Exception as e:
                        traceback.print_exc()
                    fg.get_next_file()
                else:
                    fg.get_next_file()
        except Exception as e:
            #f.close()
            traceback.print_exc()
    except Exception as e:
        traceback.print_exc()
    
def get_cursor(start_chunk, testing=False):
    latest_files = os.listdir('./index_vecs/last_cursors/')
    uid = None
    #Find the latest uid
    for file in latest_files:
        if not(os.path.isdir(f'./index_vecs/last_cursors/{file}')):
                #print(file.find(str(start_chunk)))
                if (file.find('_' + str(start_chunk) + '_') != -1):
                    with open(f'./index_vecs/last_cursors/{file}') as f:
                        prev_uids = f.readlines()
                        prev_uids.sort()
                        if prev_uids is not None and len(prev_uids) > 0:
                            uid = prev_uids[-1].replace('\n', '')
                            #print(start_chunk, '  ', uid)
    if not(testing) and uid is not None:
        old_backups = os.listdir('./index_vecs/last_cursors/backup_cursors/')
        for file in old_backups:
            os.remove(f'./index_vecs/last_cursors/backup_cursors/{file}')
        for file in latest_files:
            if not(os.path.isdir(f'./index_vecs/last_cursors{file}')):
                shutil.move(f'./index_vecs/last_cursors/{file}', f'./index_vecs/last_cursors/backup_cursors/{file}')

    with open(f'./index_vecs/last_cursors/_{start_chunk}_{uid}.txt', 'a') as f:
        if uid is not None:
            f.write(uid)
            f.write('\n')
        else:
            pass
    return uid


def get_latest_cursors(max_procs,testing=False):
    import shutil
    latest_files = os.listdir('./index_vecs/last_cursors/')
    uids = []
    for file in latest_files:
        if not(os.path.isdir(f'./index_vecs/last_cursors/{file}')): 
            with open(f'./index_vecs/last_cursors/{file}') as f:
                prev_uids = f.readlines()
                prev_uids.sort()
                last_cursor = str(prev_uids[-1]).replace('\n', '')
                uids.append(last_cursor)
    if not(testing):
        old_backups = os.listdir('./index_vecs/last_cursors/backup_cursors/')
        for file in old_backups:
            os.remove(f'./index_vecs/last_cursors/backup_cursors/{file}')
        for file in latest_files:
            if not(os.path.isdir(f'./index_vecs/last_cursors/{file}')):
                shutil.move(f'./index_vecs/last_cursors/{file}', f'./index_vecs/last_cursors/backup_cursors/{file}')
    return uids

"""
Start a Pool of workers and get them to each handle making indexes for a section of the directories.
"""
def main():
    # Number of worker processes (adjust as needed)
    num_processes = multiprocessing.cpu_count()

    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=num_processes)
    dirs = os.listdir('/home/tripptd/spotify/audio_analysis/')
    dirs.sort()
    chunk_size = int(len(dirs) / num_processes)
    chunk_lens = []
    start_idxs = []
    start_idx = 0
    while dirs:
        start_idxs.append(start_idx)
        chunk_lens.append(len(dirs[:chunk_size]))
        start_idx += len(dirs[:chunk_size])
        dirs = dirs[chunk_size:]
    #chunk_starts = [start_idx+chunk_len for (start_idx, chunk_len) in zip(start_idx, chunk_lens)]
    #cursors = get_latest_cursors(num_processes, testing=True)
    #cursors = [None] * num_processes
    #cursors.sort()
    #print(cursors)
    # Start reading files concurrently
    for (start_idx, chunk_len) in zip(start_idxs, chunk_lens):
        #print('starting: ', start_idx, ' at: ', cursor)
        pool.apply_async(init_workers, args=(start_idx, start_idx+chunk_len))

    pool.close()
    pool.join()
    # Close the pool and wait for all processes to completed

if __name__ == "__main__":
    main()
