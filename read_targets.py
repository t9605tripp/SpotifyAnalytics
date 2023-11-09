import multiprocessing
import os
import numpy as np
from simhash import SimHash
import file_getter
from filelock import FileLock
import jsonlines
import pandas as pd
import time
from functools import reduce

def check_bounds():
    pass

def query_run(start_ms, end_ms, uid):
    """
    get the original segment data by reading the query file
    """
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    indexes = np.load(selected_hash_fp)[0:16,:]
    hasher = SimHash(indexes)
    #dirs = os.listdir('/home/tripptd/spotify/audio_analysis/')
    start_chunk = 0
    end_chunk = len(dirs)
    fg = file_getter.FileGetter(start_chunk, end_chunk, uid)
    segs = fg.segs
    query_segs = []
    seg_idxs = []
    for sidx, seg in enumerate(segs):
        start_time = seg['start']
        end_time = start_time + seg['duration']
        curr_start_ms = start_time * 1000
        curr_end_ms = end_time * 1000
        if curr_end_ms > start_ms and curr_start_ms < end_ms:
            seg_idxs.append(sidx)
            query_segs.append(seg)
            #print('seg ms: ', curr_start_ms, ' | ', curr_end_ms)
            #print('query ms: ', start_ms, ' | ', end_ms)
    #query_dir = './index_vecs/64_robust_float32_query/'
    #print('there are ', len(query_segs), ' query segs')
    # line = [sidx, uid]
    """
    Get all the matches, add average (abs) distance from original seg idx as a column
    first, x = orig_sidx - match_sidx
    for each x in uid, summarize then divide by count to get the average distance.
    this should level the matches between a song that matches often, but poorly with a song that matches very well once.
    stack each of these uid | average dist features into a series.
    """
    #matches = {}
    #multiprocessing here?
    #reformat everything to a .npy?
    lots_of_data = []
    start_all = time.time()
    for orig_sidx, query_seg in zip(seg_idxs,query_segs):
        start = time.time()
        #matches[orig_sidx] = {} 
        byte_data, hex_dir = hasher.hash(query_seg)
        match_file = query_dir + '/' + hex_dir[0] + '/' + hex_dir[1] + '/matches.jsonl'
        if (os.path.exists(match_file)):
            #print(hex_dir[0] + ' ' + hex_dir[1] + ' size: ' + str(os.path.getsize(match_file) / 32))
            df = None
            lock = FileLock(query_dir + '/' + hex_dir[0] + '/' + hex_dir[1] + '/match.lock')
            with lock:
                sidxs = []
                uids = []
                with open(match_file, 'r') as f:
                    lines = f.readlines()
                    lines = [line.strip('\'[]\n') for line in lines]
                    sidxs = [int(line.split(',')[0]) for line in lines]
                    uids = [str(line.split(',')[1]) for line in lines]
                data = {'sidx': sidxs, 'uid': uids}
                df = pd.DataFrame(data)
                #df['sidx'] = df['sidx'].astype(np.uint16)
                #df['uid'] = df['uid'].astype(np.str_)
                #print(df.dtypes)
                df['diff'] = df['sidx'] - orig_sidx
                #df['diff'] = df['sidx'].apply(lambda x: abs(x - orig_sidx))
                #print('df after diff:\n', df.head)
                group_diff = df.groupby(['uid'], as_index=False)['diff'].sum()
                #print(group_diff.index)
                #print(df.columns)
                group_diff.columns = ['uid', 'diff']
                #print('group diff:\n', group_diff.head) 
                group_ct = df.groupby(['uid'], as_index=False).size()
                #print('group ct:\n', group_ct.head)
                group_ct.columns = ['uid', 'ct']
                grouped = group_diff.merge(group_ct, how='left', on='uid')
                grouped[f'avg_{orig_sidx}'] = grouped['diff'] / grouped['ct']
                lots_of_data.append(grouped[['uid', f'avg_{orig_sidx}']])
                #df.sort_values(by='uid')
                #print(grouped.head)
                 
            #lots_of_data.append(df)
        end = time.time()
        print(orig_sidx, " searched in: ", end-start)
    """
    sort df list by number of matches to maximize left joins.
    check number of nans, the less nans the better.
    a single nan means it is always more distant than other matches.. for now.. 
    """
    end_all = time.time()
    print("all searched in: ", end_all-start_all)
    sorted_list = sorted(lots_of_data, key=lambda x: x.shape[0])
    df = reduce(lambda x,y: pd.merge(x, y, how='left', on='uid'), sorted_list)
    df['nans'] = df.isna().sum(axis=1)
    max_nans = len(sorted_list)
    result_pending = True
    num_nans = 0
    res = None
    while result_pending:
        res = df.loc[df['nans'] == num_nans]
        res_size = res.shape[0]
        if res_size > 0 or num_nans > max_nans:
            result_pending = False
        num_nans += 1
    print('reduced to best: ', res.head(10), res.columns[1:])
    """
    Now we need to identify the top N best songs..
    """
    res['mean_diff'] = res[res.columns[1:-1]].mean(axis=1)
    print(res[['uid','mean_diff']].sort_values(['mean_diff']).head(50).to_json(orient='records'))
    return  
if __name__ == "__main__":
    query_run(50000, 51000, '11LmqTE2naFULdEP94AUBa')
