import gzip
import os
import json
import random
import numpy as np
import time
import pandas as pd
import logging
from tqdm import tqdm
#def get_folders():
#    for folder in os.listdir("~/spotify/audio_features"):
#        if os.path.isdir(folder):
#            print(folder)
#'7tvuLLroI0n6uYBWuFig5d'
#print(os.listdir('/home/tripptd/spotify/audio_analysis/7tv'))
#I could possibly read a subset of bytes?

logging.basicConfig(filename='./logs/preprocessing.log', encoding='utf-8', level=logging.DEBUG)
miss_ct = 0


timbre_dt = np.dtype([('t1', np.float32), ('t2', np.float32),
        ('t3', np.float32), ('t4', np.float32), ('t5', np.float32), ('t6', np.float32),
        ('t7', np.float32), ('t8', np.float32), ('t9', np.float32), ('t10', np.float32),
        ('t11', np.float32), ('t12', np.float32), ('seg_start', np.float32),
        ('seg_dur', np.float32), ('seg_idx', np.float32)])

"""
#inspiration from google's generative AI
We only have a subset, but it's still a ton of data.
"""
def random_dir(fpath):
    global miss_ct
    """
    Generates the directory randomly from the bounds in ~/spotify/audio_analysis
    """
    found_dir = ''
    not_found = True
    while not_found:
        random_dir_num = ''.join(random.choice('01234567'))
        random_dir_let = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for _ in range(2))
        random_dir = random_dir_num + random_dir_let
       
        try:
            os.path.exists(fpath + random_dir + '/')
            found_dir = ''.join(random_dir)
            not_found = False
        except IsADirectoryError as e:
            logging.debug(str(e))
            not_found = True
            miss_ct += 1
    return found_dir
"""
#ripped from google's generative AI bot, oops no sources? I don't think it's using old LSH...
The file names are just picked out of these random chars, and they are 22 chars long including the dirname.
"""
def random_fname(dir_name):
  """Generates a random base 62 uid of the specified length.
  """
  # Generate a random string of the specified length.
  fname = dir_name + ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for _ in range(19))

  return fname


"""
This should always find a file if the directory is good,
selects a random existing file from the dir
technically could hit the same file twice for now 10SEP
"""
def random_file_selection(dir_path):
    global miss_ct
    fname = ''
    try:
        files = os.listdir(dir_path)
        fname += random.choice(files)
        file_not_found = False
    except FileNotFoundError as e:
        logging.debug(str(e))
    return fname

"""
gather the full filepath to a random uid that exists and return to main for open_gz to use
"""
def get_random_filepath():
    fpath_begin = '/home/tripptd/spotify/audio_analysis/'
    file_not_found = True
    fpath = ''
    uid = ''
    dir_name = ''
    while file_not_found:
        fpath += fpath_begin
        dir_name = random_dir(fpath)
        fpath += dir_name + '/'
        selected_file = random_file_selection(fpath)
        if selected_file != '':
            fpath += selected_file
            uid += fpath[-30:-8]
            file_not_found = False
        else:
            dir_name = ''
            fpath = ''
    return fpath, uid
"""
Crack open the zip and read the juice.
set timer counts time to read files and places them in a dict in main
"""
def open_gz(file_path):
    global miss_ct
    start = time.time()
    try: 
        with gzip.open(file_path, 'rb') as f:
            bytes_data = f.read()
            audio_analysis = json.loads(bytes_data)
            #print(audio_analysis.keys())
            #dict_keys(['meta', 'track', 'bars', 'beats', 'sections', 'segments', 'tatums'])
            end = time.time()
            duration = end - start
            #print(type(audio_analysis['segments'][0]['timbre'][0]))
            return audio_analysis['segments'], duration
    except Exception as e:
        logging.debug(str(e))
        miss_ct += 1
        return 0,0        
    #I want to find the statistics around timbre data distribution, and seg index.
    #start accumulating as fast as you can bud.
       #print(segments[0])
       #type(timbre data) = float 
       # {'start': 0.0, 'duration': 0.39197, 'confidence': 0.0, 'loudness_start': -60.0, 'loudness_max_time': 0.0, 'loudness_max': -60.0,
       #    'loudness_end': 0.0, 'pitches': [0.274, 0.247, 0.278, 0.321, 0.609, 1.0, 0.478, 0.263, 0.29, 0.275, 0.314, 0.279],
       #    'timbre': [0.0, 171.13, 9.469, -28.48, 57.491, -50.067, 14.833, 5.359, -27.228, 0.973, -10.64, -7.228]}
        
    #for chunk in iter(lambda: f.read(1024), b''):
    #print(chunk)
#

"""
init a dict for storing fread times
"""
def init_timer_dict():
    timer_dict = {}
    #timer_dict.setdefault('idx',[])
    timer_dict.setdefault('runtime',[])
    timer_dict.setdefault('uid',[])
    timer_dict.setdefault('seglen',[]) 
    return timer_dict
"""
insert a record for fread
"""
def insert_timer(timer_dict, rt, uid, seglen):
    timer_dict['runtime'].append(rt)
    timer_dict['uid'].append(uid)
    timer_dict['seglen'].append(seglen)
    return

def insert_timbre_data(timbre_vec_stats, curr, segments):
     #python floats are 32 bit, and so is time.time() and timbre data, duration, start
    #([('t1', np.float32), ('t2', np.float32),
    #    ('t3', np.float32), ('t4', np.float32), ('t5', np.float32), ('t6', np.float32),
    #    ('t7', np.float32), ('t8', np.float32), ('t9', np.float32), ('t10', np.float32),
    #    ('t11', np.float32), ('t12', np.float32), ('seg_start', np.float32),
    #    ('seg_dur', np.float32), ('seg_idx', np.int64)])
    #if (len(segments) + curr > len(timbre_vec_stats)):
    #    print("ending on this round, begin at: ", curr)
    for idx, seg in enumerate(segments):
        if (len(timbre_vec_stats) > curr+idx):
            #print(type(seg['start']))
            #print(type(seg['duration']))
            timbre_vec_stats[curr+idx] = (seg['timbre'][0],seg['timbre'][1],seg['timbre'][2],
                seg['timbre'][3],seg['timbre'][4],seg['timbre'][5],seg['timbre'][6],seg['timbre'][7],
                seg['timbre'][8],seg['timbre'][9],seg['timbre'][10],seg['timbre'][11], seg['start'], seg['duration'], idx)
    return

def first_attempt():
    global miss_ct
    timbre_vec_stats = np.empty([200000,1],dtype=timbre_dt)
    read_data_timer = init_timer_dict()
    file_read_ct = 0
    timbre_vec_stats_idx = 0
    curr_timbre_vec = 0
    log_name = ''
    file_ct = 10000
    pbar = tqdm(total = file_ct)
    while file_read_ct < file_ct:
        fp, uid = get_random_filepath()
        segments, runtime = open_gz(fp)
        if segments:
            seglen = len(segments)
            insert_timer(read_data_timer, runtime, uid, seglen)
            insert_timbre_data(timbre_vec_stats, curr_timbre_vec, segments)
            curr_timbre_vec+=seglen
            if file_read_ct < 1:
                log_name += uid
            file_read_ct+=1
            pbar.update(1)
    kvp = read_data_timer.items()
    logging.debug(f'{log_name}_total_{file_ct}_missed_{miss_ct}')
    np.save(f'./logs/timbre/{uid}_timbre_{file_read_ct}_ct.npy', timbre_vec_stats[:,:curr_timbre_vec])
    with open(f'./logs/freads/{uid}_freads_{file_read_ct}_ct.json','w') as f:
        json.dump(read_data_timer, f, indent=4)
    pbar.close()

def get_random_seg():
    fp, uid = get_random_filepath()
    segments, runtime = open_gz(fp)
    seg = None
    if segments:
        seg = random.choice(segments)
    return seg

def get_timbre_bound_point():
    seg = get_random_seg()
    return np.array([seg['timbre'][0], seg['timbre'][1], seg['timbre'][2], seg['timbre'][3],
        seg['timbre'][4], seg['timbre'][5], seg['timbre'][6], seg['timbre'][7], seg['timbre'][8],
        seg['timbre'][9], seg['timbre'][10], seg['timbre'][11]]).astype(np.int16)

#currently only returns np.int16, but could make this variable precision
def get_timbre_bound_data():
    import psutil
    print(psutil.virtual_memory())
    max_segs = 100000
    timbre_bounds = np.empty([max_segs,12],dtype=np.int16)
    seg_ct = 0
    pbar = tqdm(total = max_segs)
    while seg_ct < max_segs:
        timbre_bounds[seg_ct,] = get_timbre_bound_point()
        pbar.update(1)
    pbar.close()
    return timbre_bounds

def main():
    print(get_timbre_bound_data())

if __name__ == "__main__":
    main()


#Hash considerations, 
#I could use banding.
#I could include the segment index in the hash?

#LSH ideas
#Vector for timbre is 12-vec
#Additional layers can be added later depending on the performance.
#If I can preprocess these fast enough, I could try several methods.
#uniformly generate a random vector of size 12 with limits same as timbre? []

#technically they are unbounded.
# I should build a statistics around this.
