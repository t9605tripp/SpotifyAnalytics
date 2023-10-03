import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import binarize
from multiprocessing import Lock
"""
ONE BYTE AT A TIME 
"""
class SimHash:
    def __init__(self, indexes):
        #self.match_dt = np.dtype([('uid', np.unicode_, 22), ('sidx', np.uint16)])
        self.indexes = indexes
        #self.uid = uid
        #self.save_fp = './index_vecs/64_robust_float32_query/'
        #self.shared_lock = lock

    def hash(self, seg):
        timbre_vec = np.array(seg['timbre'], dtype=np.float32).reshape(1,-1)
        similarity_scores = cosine_similarity(timbre_vec, self.indexes)
        byte_data = self.get_bytes(similarity_scores)
        hex_dirs = []
        for b in byte_data:
            hex_dirs.append(b.tostring().hex())
        return byte_data,hex_dirs

    def get_bytes(self, similarity_scores):
        res = np.sign(similarity_scores)
        res[res<0] = 0
        res = res.astype(np.uint8)
        byte_data = np.packbits(res)
        return byte_data
