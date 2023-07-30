import spotipy
#import remix
#import timbre_search
#from spotipy import SpotifyClientCredentials
#import json
import networkx as nx
import matplotlib.pyplot as plt

#mostly for networkx stuff, traversal and evaluating the graph.

#simple, writes the newfound recommended to my local edgelist 
#I try colliding my edgelist later.
def get_recommendations(spotify, H, seed, degree, depth):
    if depth > 5:
        return False
    #actually it's hard to test that so I'm not doing it currently.
    #don't build more if it's present in the current graph, checking degree as well.
    # search_tracks = [seed]
    # for deg in range(1,degree+1):
        # neighbors = H.adj[seed]
        # if H.has_node(seed):
            # return list(H.adj[seed])
    #start with new G, not filled.
    G = nx.read_edgelist('entry.edgelist')
    if not(G.has_node(seed)):
        G.add_node(seed)
    #we will always build out more recommendations
    search_tracks = [seed]
    new_search = []
    for deg in range(1,degree+1):
        #print("searching for: ", search_tracks)
        #print("finding degree ", deg)
        pop_amt = len(search_tracks)
        for strack in search_tracks:
            #limited to 10 new each time. This exponentially grows so don't turn the degree up much.
            recommended = spotify.recommendations(seed_tracks=[strack], limit = 10)
            #add to the graph
            new_search.clear()
            for rtrack in recommended['tracks']:
                
                #print(rtrack['id'], "-->", strack)
                G.add_node(rtrack['id'])
                G.add_edge(strack, rtrack['id'])
                new_search.append(rtrack['id'])
            #remove pop amount 
        search_tracks = new_search
    
    #might be discontinuous.
    #keep just the new onestosearch instead of G
    for node in G:
        if node in H:
            connected_graphs = True
            #print("connected graphs!")
            nx.write_edgelist(G, 'entry.edgelist', data=False)
            return G
    #print("recursing")
    return get_recommendations(spotify, H, seed, degree, depth+1)
    
    

def find_matches(spotify, seed, degree, esize):    
    if esize == 1:
        H = nx.read_edgelist('spotify.1.edgelist')
        G = get_recommendations(spotify, H, seed, degree, 1)
    elif esize == 20:
        #takes an extraordinary amount of time.
        H = nx.read_edgelist('spotify.20.edgelist')
        G = get_recommendations(spotify, H, seed, degree, 1)
    
    #should be connected here
    try:
        Z = nx.compose(G,H)
    except:
        return False
    #adding neighbors to the return, as a dict with degree associated.
    node_ct = 0
    adj_list = {}
    node_ct += len(list(Z.adj[seed]))
    adj_list["1"] = [n for n in Z.adj[seed]]
    #.setdefault('key',[])
    #.extend or +=
    if degree > 1:
        for deg in range(2,degree+1):
            for m in adj_list[str(deg-1)]:
                node_ct += len(list(Z.adj[m]))
                #append this instead of assignment.
                adj_list[str(deg)] = [n for n in Z.adj[m]]
    #print(node_ct, " compare nodes: ", adj_list)
    return adj_list, node_ct
    #connected_nodes = nx.node_connected_component(Z, test_songs[1])
    #S = Z.subgraph(connected_nodes)
    #print(len(list(S.nodes)))
    #draw_graph(G)
    #draw_graph(H)
    #draw_graph(Z)
    #draw_graph(S)
    
#https://networkx.org/documentation/latest/auto_examples/drawing/plot_rainbow_coloring.html#sphx-glr-auto-examples-drawing-plot-rainbow-coloring-py
def draw_graph(G):  
    fig, ax = plt.subplots(figsize=(8, 8))
    nx.draw(G)
    ax.set_axis_off()
    fig.tight_layout()
    plt.show()
    
# def get_target_track():
    # spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    # artist = "Alex Stein"
    # title = "Bonfire"
    # duration=392
    # track_info = remix.find_on_spotify(spotify, artist, title, duration)
    # pretty_track_info = json.dumps(track_info, indent=2)
    # track_id = track_info['id']
    # #track_meta = remix.get_metadata(r".\Tainted Love.mp4")
    # #print(track_meta)
    # track_analysis = spotify.audio_analysis(track_id)
    
    # pretty_track_analysis = json.dumps(track_analysis, indent=4)
    # print(pretty_track_analysis)
    # with open(f'{title}_{track_id}.json', 'w') as f:
        # f.write(pretty_track_analysis)
        


#if __name__ == "__main__":
#    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
#    main(spotify)