import gzip
import os
import json
import random
import numpy as np
import logging

"""
Initialized it will be empty
call .get_random_file()
or .get_next_file() to load a file
I may split this out later, but it's fine here for now..
call .get_random_seg() to get a single segment
call .get_segs() to get all the segments
"""
class FileGetter:
    def __init__(self, start, end):
        self.fp = '/home/tripptd/spotify/audio_analysis/'
        #iterators were way too hard, so I made my own
        
        #Set up Directory Controller
        self.dir_idx = -1
        self.ordered_dirs = None
        self.dirs_len = 0
        self.curr_dir = None
        self.init_ordered_dirs(start, end)

        #Set up File Controller/Segs Controller
        self.file_idx = -1
        self.ordered_files = None
        self.files_len = 0
        self.curr_file = None
        self.segs = None
        self.init_ordered_files()
        
        #Flag Exhausted Files/Dirs
        self.exhausted_files = False
        self.exhausted_dirs = False
    """
    GET DIRS SECTION***********************************************************
    """
    def init_ordered_dirs(self,start,end):
        selected_dirs = os.listdir(self.fp)
        selected_dirs.sort()
        self.ordered_dirs = selected_dirs[start:end]
        #print(self.ordered_dirs)
        self.dirs_len = len(self.ordered_dirs)
        #print(self.dirs_len)
        self.get_next_dir()
        #print(self.curr_dir)
        return
    """
    Gets the next alphabetical existing dir
    """
    def get_next_dir(self):
        self.dir_idx+=1
        if self.dir_idx < self.dirs_len:
            self.curr_dir = self.ordered_dirs[self.dir_idx]
        else:
            self.dir_idx = -1
            self.curr_dir = None
        return
    """ 
    Get a random existing dir
    """
    def get_random_dir(self):
        self.dir_idx = random.randrange(self.dirs_len)
        self.curr_dir = self.ordered_dirs[self.dir_idx]
        self.init_ordered_files()
    """
    GET FILES SECTION**********************************************************
    """
    def init_ordered_files(self):
        selected_files = os.listdir(self.fp + self.curr_dir + '/')
        selected_files.sort()
        self.ordered_files = selected_files
        self.files_len = len(self.ordered_files)
        #print(self.ordered_files)
        self.curr_file = self.get_next_file()
        print(self.curr_file)
        return
    """
    This should always find a file if the directory is good,
    selects a random existing file from the dir
    technically could hit the same file twice for now 10SEP,23SEP
    """
    def get_random_file_from_dir(self):
        self.file_idx = random.randrange(self.files_len)
        self.curr_file = self.ordered_file[self.file_idx]
        self.segs = self.get_segs()
        if not(self.segs):
            get_random_file(self)

    def get_next_file(self):
        #print(self.file_idx)
        #print(self.files_len)
        while not(self.curr_file):
            self.file_idx += 1
            if self.file_idx < self.files_len:
                self.curr_file = self.ordered_files[self.file_idx]
            else:
                self.file_idx = -1
                self.get_next_dir()
                init_ordered_files()
            self.segs = self.get_segs()
        else:
            self.file_idx = -1
            self.get_next_dir()
            self.get_next_file()
        return

    """
    GET SEGS SECTION***********************************************************
    Crack open the zip and read the juice.
    could set a timer counts time to read files and places them in a dict in main
    """
    def get_segs(self):
        with gzip.open(self.fp + self.curr_dir + '/' + self.curr_file, 'rb') as f:
            bytes_data = f.read()
            audio_analysis = json.loads(bytes_data)
            #print(audio_analysis.keys())
            #dict_keys(['meta', 'track', 'bars', 'beats', 'sections', 'segments', 'tatums'])
            #print(type(audio_analysis['segments'][0]['timbre'][0]))
            return audio_analysis['segments']
    
    def get_random_seg(self):
        if self.segs:
            valid_seg = None
            segslen = len(self.segs)
            while not(valid_seg) and segslen > 0:
                segsles-=1
                valid_seg = random.choice(self.segs)['timbre']
        else:
            return -1
    """
    WHAT TO DO WHEN EMPTY OR EXHAUSTED??***********************************************
    """
    """
    THINGS TO DO
    """
    def get_random_timbre():
        random_timbre = None
        while not(random_timbre):
            if not(self.exhausted_dirs):
                self.get_random_dir()
                self.get_random_file_from_dir()
                if not(self.exhausted_files):
                    random_timbre = self.get_random_seg()['timbre']
        print(random_timbre)
