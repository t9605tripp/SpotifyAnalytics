import numpy
import hashlib

class SimHash:
    def __init__(self, vec, hash_bits=64):
        self.data = vec
        self.hash_bits = hash_bits
        self.hash_value = self.calculate_hash()

    def calculate_hash(self):
        hash_values = 
