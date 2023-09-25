import file_getter
import numpy as np
import os

def cycle_arrs():


def main():
    timbre_files = os.listdir('/home/tripptd/Tripp5800/SpotifyAnalytics/logs/timbre/')
    print(timbre_files)

    arr = np.load('./logs/timbre/100_timbre_data_107132.npy')
    print(arr)

if __name__ == '__main__':
    main()
