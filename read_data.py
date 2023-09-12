import numpy as np
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# https://towardsdatascience.com/the-art-of-effective-visualization-of-multi-dimensional-data-6c7202990c57

"""
Turn the timbre_arr structured array into a df for easy display, concats with other runs
"""
def get_timbre_list():
    timbre_path = './logs/timbre/'
    files_list = os.listdir(timbre_path)
    return files_list

def get_fread_list():
    fread_path = './logs/freads/'
    files_list = os.listdir(fread_path)
    return files_list

def load_df_timbre(f_selected):
    timbre_path = './logs/timbre/'
    timbre_arr = np.load(timbre_path + f_selected)
    #t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12
    #seg_start, seg_dur, seg_idx
    df = pd.DataFrame(timbre_arr.ravel())
    return df

def load_df_fread(f_selected):
    fread_path = './logs/freads/'
    with open(fread_path+f_selected,'r') as f:
        fread_dict = json.load(f)
    df = pd.DataFrame(fread_dict)
    return df

def univariate_display(df):
    df.hist(bins=10, color='steelblue', edgecolor='black', linewidth=1.0,
            xlabelsize=8, ylabelsize=8, grid=False)
    plt.tight_layout(rect=(0,0,1.2,1.2))

def correlation_heatmap(timbre_arr):
    f, ax = plt.subplots(figsize=(10,6))

def gather_dfs():
    timbre_list = get_timbre_list()
    freads_list = get_fread_list()
    datasets = {'freads': freads_list, 'timbres': timbre_list}
    return datasets

if __name__ == '__main__':
    timbre_list = get_timbre_list()
    fread_list = get_fread_list()
    timbre_df = load_df_timbre(timbre_list[0])
    fread_df = load_df_fread(fread_list[0])
    print(timbre_df)
    print(fread_df)
