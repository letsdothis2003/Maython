import random

# Global Parameters
Q = 256
DEFAULT_M = 4
DEFAULT_N = 6
DEFAULT_K = 2
DEFAULT_O = 3

def array_to_string(arr):
    return "[" + ", ".join([f"{x:02X}" for x in arr]) + "]"

def vector_mod_q(vec, q=Q):
    return [x % q for x in vec]

def generate_random_vector(length, q=Q):
    return [random.randint(0, q-1) for _ in range(length)]