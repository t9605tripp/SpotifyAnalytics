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
        
        #Set up File Controller/Segs Controller
        self.file_idx = -1
        self.ordered_files = None
        self.files_len = 0
        self.curr_file = None
        self.segs = None

        #Initialize the above items in init_ordered_dirs
        self.init_ordered_dirs(start, end)
        
        #Flag Exhausted Files/Dirs
        #self.exhausted_files = False
        self.exhausted_dirs = False
    """
    GET DIRS SECTION***********************************************************
    """
    def init_ordered_dirs(self,start,end):
        #This list of dirs will never change, start the dir_idx at 0
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
    This will also set the cursor to the first file of the dir
    """
    def get_next_dir(self):
        #Go to the next dir. If at the end, you are done trying to continue
        self.dir_idx+=1
        if self.dir_idx < self.dirs_len:
            self.curr_dir = self.ordered_dirs[self.dir_idx]
            self.init_ordered_files()
        else:
            self.dir_idx = -1
            self.curr_dir = None
            self.ordered_dirs = None
            self.exhausted_dirs = True
        return
    """ 
    Get a random existing dir
    reset the files, and set cursor to first file of dir
    """
    def get_random_dir(self):
        #Randomly select one of the dirs, init the files.
        self.dir_idx = random.randrange(self.dirs_len)
        self.curr_dir = self.ordered_dirs[self.dir_idx]
        self.init_ordered_files()
    """
    GET FILES SECTION**********************************************************
    """
    """
    After getting into a dir, this runs and inits the file list.
    If the file list is empty, ask for the next dir.
    """
    def init_ordered_files(self):
        self.file_idx = -1
        self.files_len = 0
        self.curr_file = None
        self.segs = None
        self.ordered_files = None
        selected_files = os.listdir(self.fp + self.curr_dir + '/')
        selected_files.sort()
        self.ordered_files = selected_files
        #files initialized, check for empty dir.
        if (self.ordered_files):
            #print(self.ordered_files)
            self.files_len = len(self.ordered_files)
            self.get_next_file()
        else:
            self.get_next_dir()
        return
    """
    This should always find a file if the directory is good,
    selects a random existing file from the dir
    technically could hit the same file twice for now 10SEP,23SEP
    """
    def get_random_file(self):
        self.curr_file = None
        self.file_idx = random.randrange(self.files_len)
        #print('selected:' + str(self.file_idx))
        self.curr_file = self.ordered_files[self.file_idx]
        self.get_segs()
        return 
    """
    SELECT the next valid file if it has segs
    """
    def get_next_file(self):
        self.curr_file = None
        while not(self.curr_file):
            self.file_idx += 1
            if self.file_idx < self.files_len:
                self.curr_file = self.ordered_files[self.file_idx]
                #print(self.curr_file)
                self.get_segs()
            else:
                self.file_idx = -1
                if not(self.exhausted_dirs):
                    self.get_next_dir()
                else:
                    return
        return

    """
    GET SEGS SECTION***********************************************************
    Crack open the zip and read the juice.
    could set a timer counts time to read files and places them in a dict in main
    """
    def get_segs(self):
        self.segs = None
        with gzip.open(self.fp + self.curr_dir + '/' + self.curr_file, 'rb') as f:
            bytes_data = f.read()
            audio_analysis = json.loads(bytes_data)
            #print(audio_analysis.keys())
            #dict_keys(['meta', 'track', 'bars', 'beats', 'sections', 'segments', 'tatums'])
            #print(type(audio_analysis['segments'][0]['timbre'][0]))
            self.segs = audio_analysis['segments']
        if not(self.segs):
            #print('missing segs:'+self.curr_dir+'/'+self.curr_file)
            self.get_next_file()
        #print(self.segs)
        return

    def get_random_seg(self):
        if self.segs:
            valid_seg = None
            segslen = len(self.segs)
            while not(valid_seg) and segslen > 0:
                segslen-=1
                valid_seg = random.choice(self.segs)
            return valid_seg
        else:
            return -1
    """
    OPEN FOR CALLING
    """
    def get_random_timbre(self):
        self.get_random_dir()
        #print('dir:'+str(self.curr_dir))
        #print('opts:'+str(self.files_len))
        self.get_random_file()
        #print('dir:'+str(self.curr_dir))
        #print('file:'+str(self.curr_file))
        #GET a random segment from that file
        random_timbre = self.get_random_seg()['timbre']
        #Return the timbre part
        return random_timbre

    def get_next_segs():
        self.get_next_file()
        return self.segs
