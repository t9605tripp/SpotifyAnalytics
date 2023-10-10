import file_getter
import numpy as np
import os

def save_cursors():
    uids = ['5qC0sADsjgS4sb9MQXNQ07','5By31k3HhF2GGjq82fnZCn','0eH2Bi1YX19ncnb6ZbcfY8',
            '78h3IKxvFwEPZHb0xrwR56','0019J5Mka33ek6gwzmsKBM','1IW074I5fV1liCroXGKpq4',
            '4XiYMEcHCwYGk18qqUc5ZK','6US1N1QBbiykyysRjIptRE','2b01VBINHPdpVWWECJIUMn',
            '1wl1homd5sZvDmaJukWd0p','3FEO8pE1OlBakhHn0jcHFz','3tU4XjiEEXmgHWW5tukrAR']
    for uid in uids: 
        last_dir = uid[0:3]
        with open(f'./index_vecs/last_cursors/{last_dir}.txt', 'w') as f:
            f.write(uid)

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
                print(f'{save_fp}{match_dir}/{full_match}/matches.npy is empty')
                os.remove(f'{save_fp}{match_dir}/{full_match}/.lock')
                os.remove(f'{save_fp}{match_dir}/{full_match}/matches.npy')
                os.rmdir(f'{save_fp}{match_dir}/{full_match}/')
                            #print(arr)
    print('total dirs: ', total_dirs)
    print('total_records: ', total_records)
    
    #arr = np.load('./logs/timbre/100_timbre_data_107132.npy')
    #print(arr)

if __name__ == '__main__':
    main()
