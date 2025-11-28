import random

# --- 1. FIXED CRYPTO FIELD PARAMETER ---
# Q is fixed at 256 to simulate the F_256 field used in real MAYO implementations.
Q = 256  # Finite field size (F_256 or byte-based operations)
DEFAULT_M = 4 # Number of equations (Hash size)
DEFAULT_N = 6 # Size of signature blocks
DEFAULT_K = 2 # Number of signature blocks (Simulator is limited to K=2 for bilinear terms)

# --- 2. Utility Functions ---

def poly_eval_mod(val):
    """Applies the modulo Q operation for field arithmetic simulation (F_256)."""
    return int(round(val)) % Q

def dot_product(A, B):
    """
    Simulates a vector or matrix dot product (A @ B).
    Handles both Matrix * Vector and Vector.T * Vector using standard arithmetic.
    """
    if isinstance(A[0], list):  # Matrix * Vector (A is Matrix, B is Vector)
        result = [0] * len(A)
        for i in range(len(A)):
            for j in range(len(B)):
                result[i] += A[i][j] * B[j]
        return result
    else:  # Vector.T * Vector (A is vector, B is vector)
        sum_val = 0
        for i in range(len(A)):
            sum_val += A[i] * B[i]
        return sum_val

def vector_mod_q(vec):
    """Applies poly_eval_mod to every element of a vector."""
    return [poly_eval_mod(v) for v in vec]

def array_to_string(arr):
    """Converts array elements to a formatted string, showing up to the first 10 bytes in hex."""
    if len(arr) > 10:
        display_arr = arr[:10]
        suffix = f", ... ({len(arr) - 10} more bytes)"
    else:
        display_arr = arr
        suffix = ""
    
    # Convert to hex representation
    hex_list = [f"{v:02x}" for v in display_arr]
    return f"[{' '.join(hex_list)}]{suffix}"