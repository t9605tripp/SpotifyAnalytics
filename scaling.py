import numpy as np
import os
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.preprocessing import RobustScaler
import random
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

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
    #print("original arr")
    #print(arr)
    transformer = RobustScaler().fit(arr)
    scaled_arr = transformer.transform(arr)
    #print("scaled arr")
    #print(scaled_arr)
    return transformer, scaled_arr, arr

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
        print(f'min, max of feature {idx}', np.min(feature), ' ', np.max(feature))
        samples = np.random.default_rng().uniform(uniform_min, uniform_max, num_indexes)
        index_arr[:, idx] = samples
        print('sample selected: ', samples)
    index_arr = np.load(index_vecs_fp + f'{num_indexes}_robust_float32_indexes.npy')
    #print(index_arr)
    #np.save(index_vecs_fp + f'{num_indexes}_robust_float32_indexes', index_arr)
        #density, bin_edges = np.histogram(feature, bins=100, density=True)
        #distributions.append(density)
        #bin_edges_list.append(bin_edges)
        #print('density:')
        #print(density)
        #print('bin edges:')
        #print(bin_edges)
    #print(distributions)
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

def get_index_vec_trace(index_vec):
    # Add a 3D vector using go.Scatter3d
    vec_trace = go.Scatter3d(
        x=[0, index_vec[0]],
        y=[0, index_vec[1]],
        z=[0, index_vec[2]],
        mode='lines+markers',
        line=dict(color='lime', width=4),
        marker=dict(color='blue', size=4),
        name='Vector',
        showlegend=False
    )
    pointer_trace = go.Cone(
        x=[index_vec[0]],
        y=[index_vec[1]],
        z=[index_vec[2]],
        u=[0],
        v=[0],
        w=[0],
        sizemode='absolute',
        sizeref=0.1,
        showscale=False
    )
    return vec_trace, pointer_trace

def plotting():
    transformer, scaled_data, data = get_robust_scaled_data()
    #print(scaled_data.shape)
    #print(data.shape)

    scaled = pd.DataFrame(scaled_data)
    #original = pd.DataFrame(data)
    #col_names = ['t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12']
    scol_names = ['scaled_t1', 'scaled_t2', 'scaled_t3', 'scaled_t4', 'scaled_t5', 'scaled_t6', 'scaled_t7', 'scaled_t8', 'scaled_t9', 'scaled_t10', 'scaled_t11', 'scaled_t12']
    scaled.columns = scol_names
    #original.columns = col_names

    #concat_df = pd.concat([original, scaled], axis=1)
    index_arr = np.load('./index_vecs/'+ f'64_robust_float32_indexes.npy')
    #fig = px.histogram(scaled.head(10000), x=scol_names, marginal='rug', nbins=100, histnorm='probability density') 
    #pio.write_html(fig, 'original_histograms.html')
    #pio.write_html(fig, 'scaled_histograms.html') 
    """GET 3d ORIGNal
    original = original.head(10000)
    original['avg'] = (original["t1"] + original["t2"] + original["t3"]) / 3
    fig = px.scatter_3d(original[["t1", "t2", "t3", "avg"]], x='t1', y='t2', z='t3',
              color=original['avg'])
    
    fig.update_layout(scene=dict(xaxis=dict(range=[original["t1"].min(), original["t1"].max()]), yaxis=dict(range=[original["t2"].min(), original["t2"].max()]), zaxis=dict(range=[original["t3"].min(), original["t3"].max()])))

    pio.write_html(fig, '3d_original.html')
    """
    
    scaled = scaled.head(1000)
    scaled['avg'] = (scaled["scaled_t1"] + scaled["scaled_t5"] + scaled["scaled_t11"]) / 3
    fig = go.Figure()
    config = {'displaylogo': False}
    """
    Add the planes
    """
    #Same grid for surface making.
    plane_x = np.linspace(scaled["scaled_t1"].min(), scaled["scaled_t1"].max(), 100)
    plane_y = np.linspace(scaled["scaled_t5"].min(), scaled["scaled_t5"].max(), 100)
    plane_x, plane_y = np.meshgrid(plane_x, plane_y)
    for index_vec in index_arr[0:4,:]:
        a,b,c = index_vec[0:3]
        plane_z = (-a * plane_x - b * plane_y) / c
        surf = go.Surface(x=plane_x, y=plane_y, z=plane_z, opacity=0.5, showlegend=False)
        fig.add_trace(surf)
        vec, pointer = get_index_vec_trace(index_vec[0:3])
        fig.add_trace(vec)
        fig.add_trace(pointer)
    """
    Add the point cloud
    """
    scatter_trace = go.Scatter3d(
        x=scaled["scaled_t1"],
        y=scaled["scaled_t5"],
        z=scaled["scaled_t11"],
        mode="markers",
        marker=dict(
            size=7,
            color=scaled["avg"],
            colorscale="Viridis",
            opacity=0.5
        ),
        showlegend=True
    )
    fig.add_trace(scatter_trace)
    """
    Update the axes to scale right.
    """
    fig.update_layout(showlegend=False, scene=dict(xaxis=dict(title="t1", range=[scaled["scaled_t1"].min(), scaled["scaled_t1"].max()]),
        yaxis=dict(title="t5", range=[scaled["scaled_t5"].min(), scaled["scaled_t5"].max()]),
        zaxis=dict(title="t11", range=[scaled["scaled_t11"].min(), scaled["scaled_t11"].max()])))
    fig.write_html('3d_sliced.html', config=config)
"""
    #pio.write_html(fig, '3d_scaled.html')
"""
def main():
   plotting()
   #plotting_sns_hists()
   #save_index_vecs(64)
   return

if __name__ == "__main__":
    main()
