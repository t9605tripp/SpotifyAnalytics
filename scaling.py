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

def get_robust_scaled_data():
    arr = load_scaling_data()
    transformer = RobustScaler().fit(arr)
    scaled_arr = transformer.transform(arr)
    return transformer, scaled_arr

def save_index_vecs(num_indexes):
    index_arr = np.empty((num_indexes,12), np.float32)
    index_vecs_fp = './index_vecs/'
    transformer, training_data = get_robust_scaled_data()
    features = extract_features(training_data)
    distributions = []
    bin_edges_list = []
    #ALL THE INFO FOR THE SCALING BINS
    
    for idx, feature in enumerate(features):
        uniform_min = np.min(feature)
        uniform_max = np.max(feature)
        print(np.min(feature), ' ', np.max(feature))
        samples = np.random.default_rng().uniform(uniform_min, uniform_max, num_indexes)
        index_arr[:, idx] = samples
    np.save(index_vecs_fp + f'{num_indexes}_robust_float32_indexes', index_arr)
        #density, bin_edges = np.histogram(feature, bins=100, density=True)
        #distributions.append(density)
        #bin_edges_list.append(bin_edges)
        #print('density:')
        #print(density)
        #print('bin edges:')
        #print(bin_edges)
    #print(distributions)
    #np.random.choice(training_data)
    #np.save('./index_vecs/64_index_robust_scaled_float32', index_arr)

def plotting_sns_hists():
    features = extract_features(scaled_data)
    features2 = extract_features(data)
    pid = os.getpid()
    idx = 1
    for (feature1, feature2) in zip(features, features2):
        total_records = feature1.shape[0]  
        ax = sns.histplot(data=feature1,stat='density',bins=100)
        ax = sns.histplot(data=feature2,stat='density', bins=100)
        plt.title(f't{idx}_{total_records} Comparison of Density Hist, 100 bins')
        plt.savefig(f'./scaling_hists/scaled_{idx}_{total_records}_{pid}')
        plt.clf()
        idx+=1

def main():
   save_index_vecs(64)

if __name__ == "__main__":
    main()
