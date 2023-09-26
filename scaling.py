import numpy as np
import os
from sklearn.preprocessing import RobustScaler
import random
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

def get_timbre_opts():
    opts = os.listdir('./logs/')
    return opts

#load X thousands of vectors
#Current total 25SEP: over 1500
def load_new_timbre_frame(thousand):
    scaling_files = f'./scaling_files/{thousand}_timbre_files_{pid}'
    scaling_data = f'./scaling_data/{thousand}_timbre_data_{pid}'
    sample_files = random.sample(get_timbre_opts(),thousand)
    timbre_arr = np.load('./logs/'+sample_files[0])
    file_list_arr = np.array(sample_files)
    #for later use, to associate the files with the following behemoth.
    pid = os.getpid()
    np.save(scaling_files, sample_files)
    for file in sample_files[1:]:
        thousand_data = np.load('./logs/'+file)
        timbre_arr = np.concatenate((timbre_arr, thousand_data))
        np.save(scaling_data, timbre_arr)

def get_scaling_data_opts():
    opts = os.listdir('./scaling_data/')
    return opts

def load_scaling_data():
    opts = get_scaling_data_opts()
    selection = random.choice(opts)
    scaling_data = np.load('./scaling_data/'+selection)
    #print(scaling_data)
    return scaling_data

def extract_features(data):
    features = []
    for feature_idx in range(data.shape[1]):
        feature_data = data[:, feature_idx]
        features.append(feature_data)
    return features

def make_numpy_histograms(arr):
    features = extract_features(arr)
    pid = os.getpid()
    thousand = arr.shape[1]
    scaling_hists = f'./scaling_hists/{thousand}_timbre_hists_{pid}'
    histograms = []
    for feature in features:
        hist, bin_edges = np.histogram(feature_data, bins=10, density=True)
        histograms.append((hist, bin_edges))
    np.save(scaling_hists, histograms)
    return histograms

def read_numpy_histograms():
    fp = f'./scaling_hists/'
    scaling_hists = os.listdir(fp)
    for hist in scaling_hists:
        arr = np.load(fp+hist)
        print(arr)

def make_pd(arr):
    df = pd.DataFrame(arr)
    return df

def make_graph_histograms(df_top):
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

def robust_scaling(arr):
    transformer = RobustScaler().fit(arr)
    scaled_arr = transformer.transform(arr)
    return scaled_arr

def main():
    #load_timbres(1000)
    data = load_scaling_data()
    #print(data)
    features = extract_features(data)
    print(features)
    #read_numpy_histograms()
    #df = make_pd(data)
    for idx, feature in enumerate(features):
        total_records = feature.shape[0]  
        ax = sns.histplot(data=feature,stat='density',bins=100)
        plt.savefig(f'./{idx}_{total_records}')
    #print(df.head)
    #extract_features_data()
    #transformer = RobustScaler().fit(X)
    #transformer.transform(timbre_data)

if __name__ == "__main__":
    main()
