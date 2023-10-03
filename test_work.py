import file_getter
import numpy as np
import os

def cycle_arrs():
    pass

def main():
    total_dirs = 0
    total_records = 0
    save_fp = './index_vecs/64_robust_float32_query/'
    match_8 = os.listdir(save_fp)
    match_8.sort()
    print(match_8)
    for match_dir in match_8:
        match_16 = os.listdir(save_fp + match_dir + '/')
        #print(match_16)
        for full_match in match_16:
            total_dirs += 1
            try:
                arr = np.load(save_fp + match_dir + '/' + full_match + '/matches.npy')
                total_records += arr.shape[0]
            except Exception as e:
                print(match_dir, '/', full_match)
            #print(arr)
    print('total dirs: ', total_dirs)
    print('total_records: ', total_records)
    
    #arr = np.load('./logs/timbre/100_timbre_data_107132.npy')
    #print(arr)

if __name__ == '__main__':
    main()
