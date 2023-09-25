import numpy as np
import os
from sklearn.preprocessing import RobustScaler
import random

def get_timbre_opts():
    opts = os.listdir('/home/tripptd/Tripp5800/SpotifyAnalytics/logs/')
    return opts

#load X thousands of vectors
def load_timbres(thousand):
    sample_files = random.sample(get_timbre_opts(),thousand)
    timbre_arr = np.load('./logs/'+sample_files[0])
    for file in sample_files[1:]:
        thousand_data = np.load('./logs/'+file)
        timbre_arr = np.concatenate((timbre_arr, thousand_data))
    print(timbre_arr.shape)



def main():
    load_timbres(1000)
    #transformer = RobustScaler().fit(X)
    #transformer.transform(timbre_data)


if __name__ == "__main__":
    main()
