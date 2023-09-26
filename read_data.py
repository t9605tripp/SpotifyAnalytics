import numpy as np
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math
# htitps://towardsdatascience.com/the-art-of-effective-visualization-of-multi-dimensional-data-6c7202990c57

global timbre_path = './old_logs/timbre/'
global fread_path = './old_logs/freads/'
"""
Turn the timbre_arr structured array into a df for easy display, concats with other runs
"""
def get_timbre_list():
    global timbre_path
    files_list = os.listdir(timbre_path)
    return files_list

def get_fread_list():
    global fread_path
    files_list = os.listdir(fread_path)
    return files_list

def load_df_timbre(f_selected):
    global timbre_path
    timbre_arr = np.load(timbre_path + f_selected)
    #t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12
    #seg_start, seg_dur, seg_idx
    df = pd.DataFrame(timbre_arr.ravel())
    return df

def load_df_fread(f_selected):
    global fread_path
    with open(fread_path+f_selected,'r') as f:
        fread_dict = json.load(f)
    df = pd.DataFrame(fread_dict)
    return df

def univariate_display_mpl(df):
    df.hist(bins=10, color='steelblue', edgecolor='black', linewidth=1.0,
            xlabelsize=8, ylabelsize=8, grid=False)
    plt.tight_layout(rect=(0,0,1.2,1.2))

def correlation_heatmap_mpl(timbre_arr):
    f, ax = plt.subplots(figsize=(10,6))

def gather_dfs():
    timbre_list = get_timbre_list()
    freads_list = get_fread_list()
    datasets = {'freads': freads_list, 'timbres': timbre_list}
    return datasets

#Param: fname String
#Return: freads, timbre,
def get_ftype(fname):
    split_name = fname.split('_')
    uid = split_name[2]
    ftype = split_name[1]
    return ftype

#takes an fname and returns a df for it
#make a type for the file metadata?? matching on strings for this is bad
#I could make this into an object that inits those metadata
def df_select(fname, ftype):
    df = None
    if ftype == 'freads':
        df = load_df_fread(fname)
    else:
        df = load_df_timbre(fname)
    return df

def make_chart_px(fname, graph_type):
    ftype = get_ftype(fname)
    df = df_select(fname, ftype)
    df_top = df.head(10000)
    graphJSON = None
    #numeric_columns = df.select_dtypes(include=['number'])

    if graph_type == 'histograms':
        graphJSON = make_histograms(df_top)
    else:
        #timbre df = t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12, seg_start, seg_dur, seg_idx
        #freads df = runtime, uid, seglen
        #indexes should match between the same uid so you could get runtime by seglen stats if needed.
        selected_columns = None
        if ftype == 'timbre':
            selected_columns = df[['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12']]
        elif ftype == 'freads':
            selected_columns = df[['runtime', 'seglen']]
        graphJSON = make_correlation_heatmap(selected_columns)
    return graphJSON

def make_correlation_heatmap(df):
    # Calculate the correlation matrix
    correlation_matrix = df.corr()
    fig = go.Figure(data=go.Heatmap(z=correlation_matrix.values, x=correlation_matrix.columns,
        y=correlation_matrix.columns, colorscale='Viridis'))
    # Serialize the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


#try to normalize these, make them more bayesian.
#
def make_histograms(df_top):
    total_cols = len(df_top.columns)
    #generative ai
    shape = math.ceil(math.sqrt(total_cols))
    subplot_height = 300
    figure_height = subplot_height * shape
    #vertical_spacing
    fig = make_subplots(rows=shape, cols=shape, row_heights=[subplot_height]*shape)
    # Add histograms to each subplot
    for i, column in enumerate(df_top.columns):
        row = (i // shape) + 1
        col = (i % shape) + 1
        fig.add_trace(go.Histogram(x=df_top[column], name=column), row=row, col=col)
        fig.update_xaxes(title_text=column, row=row, col=col, automargin=True)
        fig.update_yaxes(title_text='Count', row=row, col=col, automargin=True)
    # Update the layout
    fig.update_layout(title_text='Histogram Subplots', showlegend=True, height=figure_height)

    #fig = ff.create_distplot([df_top[c] for c in df.columns], df.columns)
    #fig.show()
    #fig.write_html(f'./figs/{fname}.html')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

if __name__ == '__main__':
    timbre_list = get_timbre_list()
    fread_list = get_fread_list()
    timbre_df = load_df_timbre(timbre_list[0])
    fread_df = load_df_fread(fread_list[0])
    make_chart_px(fread_df, fread_list[0])
