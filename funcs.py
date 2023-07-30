import json
import networkx as nx
import numpy as np
import build_timbre_dataset
import matplotlib.pyplot as plt
import seaborn as sns

#This file is for accessing the spotify API and returning things to the app
#app uses this file for most backend.

#search for matching tracks
def search(sp, track_info):
    result = sp.search(track_info, type='track')
    return result

#gathers a subset of the timbre given edges (seconds)
#I only use this for the target clip because i gather all the timbre for comparisons
def load_timbre_clip(spotify, track_id, start, end):
    track_analysis = spotify.audio_analysis(track_id)
    clip_length = end - start
    curr = end
    timbre_clip = []
    time_clip = []
    for seg in track_analysis['segments']:
        #stop searching after clipping the timbre section
        if curr <= 0:
            break
        if (curr <= clip_length):
            timbre_clip.append(seg['timbre'])
            time_clip.append(seg['start'])
        curr = curr - seg['duration']
    return [timbre_clip, time_clip]

#give this method a timbre clip and a full timbre to compare with a window.
#param track_info
#target = timbre
#track_info = [t_id, times, timbres]
#[0] = id, [1] = times, [2] = timbres
#ret list for one degree
#[track_id, min_diff, min_start, min_end]
def compare_timbre(target, track_info):
    #print("compare_timbre t_info: ", len(track_info))
    tgt = np.array(target)
    
    #I made the window the target size.. because that comparison makes sense
    res = []
    window_size = len(target)
    #print("window size: ", window_size)
    windowed_timbre = []
    min_diff = 2**20
    min_start = 0
    min_end = 0
    #for seg in timbre
    #tgt[:,i:i+window]
    #try using the mean
    for idx, seg in enumerate(track_info[2]):
        diff = 2**20
        #append until matching window size
        if (len(windowed_timbre) < window_size):
            windowed_timbre.append(seg)
        else:
                #Euclidean Distance between tgt and the windowed timbre from this track
                #is euclidean distance the best? Is there a way to probablistically settle that?
            diff = np.linalg.norm(tgt - np.array(windowed_timbre), axis=1)
            sum_diff = np.sum(diff)
            if (sum_diff < min_diff):
                min_diff = sum_diff
                min_end = track_info[1][idx]
                min_start = track_info[1][idx-window_size]
                #the window slides one segment at a time... could that be opened??
            windowed_timbre.pop(0)
    return [track_info[0], min_diff, min_start, min_end]

#target clip timbre and a dataset full of timbres to compare against.
#params dataset =  #rec_info = {"degree": [[t_id, times, timbres],[etc]]}
#return min_diffs = {"degree": []}
def search_timbres(target, dataset):
    #this will highlight the section of the recommended song that has min diff,
    #uses compare_timbre to compare segments
    #add some min_diffs to the dataset
    #print(dataset.keys())
    #print(dataset.values())
    min_diffs = {}
    #for each degree..
    for deg in dataset.keys():
        min_diffs[deg] = []
        #for each track in that degree
        for items in dataset[deg]:
            #use the data from dataset to make compare data
            #target = timbre
            #items = [t_id, times, timbres]
            min_diffs[deg].append(compare_timbre(target, items))
            #min_diffs = {"deg": [[track_id, min_diff, min_start, min_end], [t_id2,min2,etc],..,]}
    return min_diffs

#gathers the entire track timbre, useful for compares
#return a list [[seg_times],[seg_timbres]]
def get_track_timbre(spotify, track_id):
    track_analysis = spotify.audio_analysis(track_id)
    seg_times = [seg['start'] for seg in track_analysis['segments']]
    track_timbre = [seg['timbre'] for seg in track_analysis['segments']]
    return [seg_times, track_timbre]

#useful
#param track_list = compare_list = {"degree": [n_id,n1_id,n2_id]}
#return (deg: [(track_id, [seg_times], [seg_timbre]),(track2_info)])
def get_timbres(spotify, track_list):
    rec_info = {}
    for deg in track_list.keys():
        rec_info[deg] = []
        for track in track_list[deg]:
            track_info = get_track_timbre(spotify, track)
            #[track_info[0] - times, track_info[1] - timbres]
            rec_info[deg].append([track, track_info[0], track_info[1]])
    #rec_info = {"degree": [[t_id, times, timbres],[etc]]}
    return rec_info

#sort in ascending order
#https://stackoverflow.com/questions/3121979/how-to-sort-a-list-tuple-of-lists-tuples-by-the-element-at-a-given-index
#https://stackoverflow.com/questions/36955553/sorting-list-of-lists-by-the-first-element-of-each-sub-list
#track_id, min_diff, min_start(s), min_end(s)
def sort_mins(min_diffs):
    sorted_mins = {}
    #print(min_diffs)
    for deg in min_diffs.keys():
        sorted_mins[deg] = sorted(min_diffs[deg], key=lambda x: x[1])
    return sorted_mins
#find all mins among the compare_list
def find_min_timbre_dist(spotify, compare_list, target):
    #compare_list = {"degree": [n_id,n1_id,n2_id]}
    rec_info = get_timbres(spotify, compare_list)
    #rec_info = {"degree": [[t_id, times, timbres],[etc]]}
    #target = timbre
    min_diffs = search_timbres(target, rec_info)
    #print(min_diffs)
    mins = sort_mins(min_diffs)
    return mins

def plot_hist(diffs):
    y = np.array([np.array(degree_list) for degree_list in diffs])
    hist_plt = sns.histplot(data=y, stat='percent', kde=True)
    fig = hist_plt.get_figure()
    fig.savefig("./static/plot.png")
    
#DOES EVERYTHING
def get_matches(spotify, seed, st, et, degree, esize):
    track_uri = seed.split(":")[2]
    #gather some recommendations until collision
    found_match, compare_ct = build_timbre_dataset.find_matches(spotify, track_uri, degree, esize)
    #found_match = adj_list {"degree": [n_id,n1_id,n2_id]}
    target = load_timbre_clip(spotify, track_uri, int(st), int(et))
    #target[0] = timbre, target[1] = time
    mins = find_min_timbre_dist(spotify, found_match, target[0])
    
    #mins = {"deg": [[t_id, min_dist, starts, ends],[]], "deg2": etc}
    
    
    # #why do this? because i wanna make html table, lists are easier with Jinja
    degrees = []
    # #for each degree..
    for deg in mins.keys():
        tracks = []
        min_dists = []
        starts = []
        ends = []
        #for each track in the degree..
        for item in mins[deg]:
            tracks.append(item[0])
            min_dists.append(item[1])
            starts.append(item[2])
            ends.append(item[3])
        degrees.append([tracks, min_dists, starts, ends])
    plot_hist(min_dists)
    return mins, compare_ct 