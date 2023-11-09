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
    """
    take one seg at a time
    """
    def hash(self, seg):
        timbre_vec = np.array(seg['timbre'], dtype=np.float32).reshape(1,-1)
        similarity_score = cosine_similarity(timbre_vec, self.indexes)
        byte_data = self.get_hash_bytes(similarity_score)
        hex_dirs = []
        for b in byte_data:
            #print(b)
            hex_dirs.append(b.tostring().hex())
        return byte_data,hex_dirs
    
    """
    takes raw seg data only
    """
    def hash_all(self, segs):
        #format the timbre segments into an array.
        #EX: (1000,12)
        try:
            rows = len(segs)
            timbre_mat = np.zeros((rows,12), dtype=np.float32)
            #Load the matrix with the timbre data then cosine similarity it
            for sidx, seg in enumerate(segs):
                timbre_mat[sidx,:] = np.array(seg['timbre'], dtype=np.float32)
            similarity_scores = cosine_similarity(timbre_mat, self.indexes)
            byte_data = self.get_hash_all_bytes(similarity_scores)
            hex_dirs = []
            for idx,b in enumerate(byte_data):
                hex_chars = b.tostring().hex()
                hex_dirs.append([hex_chars[0:2], hex_chars[2:]])
            return byte_data, hex_dirs
        except Exception as e:
            return None, None

    def get_hash_bytes(self, similarity_score):
        res = np.sign(similarity_score)
        res[res<0] = 0
        res = res.astype(np.uint8)
        byte_data = np.packbits(res)
        return byte_data

    def get_hash_all_bytes(self, similarity_scores):
        res = np.sign(similarity_scores)
        res[res<0] = 0
        res = res.astype(np.uint8)
        byte_data = np.packbits(res, axis=1)
        return byte_data
