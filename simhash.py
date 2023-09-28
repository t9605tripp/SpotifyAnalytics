import numpy
import os

class SimHash:
    def __init__(self, indexes):
        self.indexes = indexes
        print(self.indexes)
    def hash(self, segs):
        #We want to save the result into a filepath
        for idx, seg in enumerate(segs):
            cosine_similarity = np.dot(vector1, vector2) / np.linalg.norm(vector1) / np.linalg.norm(vector2)
            conf = seg['confidence']
            timbre_vec = seg['timbre'])
        #np.apply_along_axis()
        
