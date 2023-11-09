import file_getter
import numpy as np
import os
import jsonlines
import time

def show_bin_edges():
    dirs = os.listdir('/home/tripptd/spotify/audio_analysis/')
    dirs.sort()
    dir_copy = os.listdir('/home/tripptd/spotify/audio_analysis/')
    dir_copy.sort()
    chunk_size = int(len(dirs) / 11)
    chunk_lens = []
    start_idxs = []
    start_idx = 0
    end_idxs = []
    end_idx = 0
    dir_names = []
    while dirs:
        start_idxs.append(start_idx)
        chunk_len = len(dirs[:chunk_size])
        chunk_lens.append(chunk_len)
        end_idx += chunk_len
        end_idxs.append(end_idx)
        start_idx += chunk_len
        dirs = dirs[chunk_size:]
    print('start chunks: ', start_idxs)
    print('end chunks: ', end_idxs)
    print('chunk lens: ', chunk_lens)
    for (start_idx, end_idx) in zip(start_idxs, end_idxs):
        first_dir = dir_copy[start_idx]
        last_dir = dir_copy[end_idx-1]
        print(start_idx, '-- ', first_dir,':',last_dir)
    
def main():
    total_dirs = 0
    total_records = 0
    save_fp = './index_vecs/64_robust_float32_query/'
    match_8 = os.listdir(save_fp)
    match_8.sort()
    print(match_8)
    for match_dir in match_8:
        match_16 = os.listdir(save_fp + match_dir + '/')
        #print(match_16)
        for full_match in match_16:
            total_dirs += 1
            try:
                arr = np.load(save_fp + match_dir + '/' + full_match + '/matches.npy')
                total_records += arr.shape[0]
            except Exception as e:
                print(f'{save_fp}{match_dir}/{full_match}/matches.npy is empty')
                os.remove(f'{save_fp}{match_dir}/{full_match}/.lock')
                os.remove(f'{save_fp}{match_dir}/{full_match}/matches.npy')
                os.rmdir(f'{save_fp}{match_dir}/{full_match}/')
                            #print(arr)
    print('total dirs: ', total_dirs)
    print('total_records: ', total_records)
 
    #arr = np.load('./logs/timbre/100_timbre_data_107132.npy')
    #print(arr)
def read_progress():
    total_dirs = 0
    total_match_files = 0
    total_size = 0
    save_fp = './index_vecs/64_robust_float32_query/'
    match_8 = os.listdir(save_fp)
    match_8.sort()
    print(match_8)
    for match_dir in match_8:
        match_16 = os.listdir(save_fp + match_dir + '/')
        #print(match_16)
        for full_match in match_16:
            total_dirs += 1
            
            fpath = f'{save_fp}{match_dir}/{full_match}/matches.jsonl'
            if os.path.exists(fpath):
                fsize = os.path.getsize(fpath)
                #print(fpath, ' size: ', fsize) 
                total_size += fsize
    print('total dirs: ', total_dirs)
    print('total_bytes: ', total_size)
    print('total records: ', total_size / 25)

def get_total_segs():
    total_dirs = 0
    total_match_files = 0
    total_size = 0
    save_fp = './index_vecs/64_robust_float32_query/'
    match_8 = os.listdir(save_fp)
    match_8.sort()
    #print(match_8)
    for match_dir in match_8:
        match_16 = os.listdir(save_fp + match_dir + '/')
        #print(match_16)
        for full_match in match_16:
            total_dirs += 1
            
            fpath = f'{save_fp}{match_dir}/{full_match}/matches.jsonl'
            if os.path.exists(fpath):
                fsize = os.path.getsize(fpath)
                #print(fpath, ' size: ', fsize) 
                total_size += fsize
    #print('total dirs: ', total_dirs)
    #print('total_bytes: ', total_size)
    #print('total records: ', total_size / 25)
    #record: '["22CHARLONGTHINGstheuid", 600] bytes vary depending on the seg idx'
    record_ct = total_size / 32
    return record_ct

def print_dirs():
    self.fp = '/home/tripptd/spotify/audio_analysis/'

def get_total_songs():
    return get_total_segs() / 1000

def get_velocity(samples=100):
    times = []
    segments_processed = []
    for x in range(samples):
        start = time.time()
        size1 = get_total_segs()
        size2 = get_total_segs()
        end = time.time()
        total = end - start
        segs = size2 - size1
        times.append(total)
        segments_processed.append(segs)
    avg_segs = sum(segments_processed) / len(segments_processed)
    avg_time = sum(times) / len(times)
    #print(avg_segs, 'segments in ', avg_time)
    per_second = avg_segs / avg_time 
    print('per second: ', per_second)
    per_day = per_second * 86400
    print('per day: ', per_day)
    songs_per_day = per_day / 1000
    print('songs per day: ', songs_per_day)
if __name__ == '__main__':
    print('conservative estimate of songs: ', get_total_songs())
    print('current velocity estimate: ')
    print(get_velocity(100))
