import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import binarize

"""
ONE BYTE AT A TIME 
"""
class SimHash:
    match_dt = np.dtype([('uid', np.unicode_, 22), ('sidx', np.int_), ('conf', np.float32)])
    def __init__(self, indexes, uid):
        self.indexes = indexes
        self.uid = uid
        #print(self.indexes)
    def hash(self, segs):
        #We want to save the result into a filepath
        save_fp = './index_vecs/64_robust_float32_query/'
        pid = os.getpid()
        for idx, seg in enumerate(segs):
            if idx < 1:
                conf = seg['confidence']
                timbre_vec = np.array(seg['timbre'], dtype=np.float32).reshape(1,-1)
                #print(f'{pid}_timbre: ', timbre_vec)
                #print(f'{pid}_indexes:', self.indexes)
                similarity_scores = cosine_similarity(timbre_vec, self.indexes)
                #print(f'{pid}_sim:', similarity_scores)
                byte = self.get_byte(similarity_scores)
                print(byte.tostring().hex())


    def get_byte(self, similarity_scores):
        res = np.sign(similarity_scores)
        res[res<0] = 0
        res = res.astype(np.uint8)
        #print(res)
        byte = np.packbits(res)
        return byte
