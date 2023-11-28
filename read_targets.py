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

def get_seg():
    pass

def euclidean(df, fg, new_uid):
    print(fg.get_uid())
    print(df)
    print(new_uid)
    return 1
def query_run(start_ms, end_ms, uid):
    """
    get the original segment data by reading the query file
    """
    selected_hash_fp = './index_vecs/64_robust_float32_indexes.npy'
    indexes = np.load(selected_hash_fp)[0:16,:]
    hasher = SimHash(indexes)
    dirs = os.listdir('/home/tripptd/spotify/audio_analysis/')
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
    query_dir = './index_vecs/64_robust_float32_query/'
    print('there are ', len(query_segs), ' query segs between ', start_ms, '-', end_ms)
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

    #ignore query segments with loudness less than some threshold.
    #1 / len(df)
    #Change the previewers to a table with the info, use a link instead of a form
    #display graphs on the results page about the hits.

    lots_of_data = []
    start_all = time.time()
    for orig_sidx, query_seg in zip(seg_idxs,query_segs):
        start = time.time()
        #matches[orig_sidx] = {} 
        byte_data, hex_dir = hasher.hash(query_seg)
        #match_file = query_dir + '/' + hex_dir[0] + '/' + hex_dir[1] + '/matches.jsonl'
        match_file = query_dir + '/' + hex_dir[0] + '/' + hex_dir[1] + '/matches.parquet'
        if (os.path.exists(match_file)):
            #print(hex_dir[0] + ' ' + hex_dir[1] + ' size: ' + str(os.path.getsize(match_file) / 32))
            df = None
            """Read Parquet
            """
            lock = FileLock(query_dir + '/' + hex_dir[0] + '/' + hex_dir[1] + '/match.lock')
            with lock:
                df = pd.read_parquet(match_file)    
                #df.info(verbose=True)
                #print(query_seg)
            df['diff'] = df['sidx'] - orig_sidx
            df['orig_sidx'] = orig_sidx
            lots_of_data.append(df)
        end = time.time()
        print(orig_sidx, " searched in: ", end-start)
    end_all = time.time()
    print("all searched in: ", end_all-start_all)
    #I found that just grouping by id and finding max hits was bad.
    #It matches on "Noise Wall" songs a lot.
    res = pd.concat(lots_of_data, axis=0, ignore_index=True)
    #res = res.sort_values('diff')
    #print(res.head)
    grouped = res.groupby([['uids','diff']], as_index=False).size()
    grouped = grouped.sort_values('size',ascending=False).head(50)
    #print(res.head)
    print(grouped)

    #THIS is where I matched on Noise Walls:
    #print(res.head(20))
    #grouped = res.groupby(['uids'], as_index=False)
    #grouped = grouped.sort_values(by='size', ascending=False)
    #top_matches = grouped.head(50)
    
    uids = grouped['uids'].to_list()
    uris = ['spotify:track:' + uid.strip(' \"') for uid in uids]
    scores = grouped['size'].to_list()
    """
    Now we need to identify the top N best songs..
    """
    """
    res['mean_diff'] = res[res.columns[1:-1]].mean(axis=1)
    print(res[['uid','mean_diff']].sort_values(['mean_diff']).head(50).to_json(orient='records'))
    """
    return uris, scores
if __name__ == "__main__":
    #Strobe
    query_run(70000, 77000,'0pgEx0eQPVh3fDpJcP4BqL')
    #Heart In Box Nirvana
    #query_run(50000, 55000, '11LmqTE2naFULdEP94AUBa')
    #Alabama Shakes - Hold On
    #query_run(29000, 34000, '436bx0eHJS5DPgIyfsDU31')
