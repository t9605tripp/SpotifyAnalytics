import numpy as np

timbre_dt = np.dtype([('t1', np.float32), ('t2', np.float32),
        ('t3', np.float32), ('t4', np.float32), ('t5', np.float32), ('t6', np.float32),
        ('t7', np.float32), ('t8', np.float32), ('t9', np.float32), ('t10', np.float32),
        ('t11', np.float32), ('t12', np.float32), ('seg_start', np.float32),
        ('seg_dur', np.float32), ('seg_idx', np.float32)])
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
def get_random_seg():
    fp, uid = get_random_filepath()
    segments, runtime = open_gz(fp)
    seg = None
    if segments:
        seg = random.choice(segments)
        if seg['timbre'][0]:
            return seg
        else:
            return get_random_seg()
           


def get_timbre_bound_point():
    seg = get_random_seg()
    return np.array([seg['timbre'][0], seg['timbre'][1], seg['timbre'][2], seg['timbre'][3],
        seg['timbre'][4], seg['timbre'][5], seg['timbre'][6], seg['timbre'][7], seg['timbre'][8],
        seg['timbre'][9], seg['timbre'][10], seg['timbre'][11]]).astype(np.int16)

#currently only returns np.int16, but could make this variable precision
def get_timbre_bound_data():
    #import psutil
    #print(psutil.virtual_memory())
    max_segs = 100000
    timbre_bounds = np.empty([max_segs,12],dtype=np.int16)
    seg_ct = 0
    #pbar = tqdm(total = max_segs)
    while seg_ct < max_segs:
        timbre_bounds[seg_ct,] = get_timbre_bound_point()
        #pbar.update(1)
    #pbar.close()
    return timbre_bounds

