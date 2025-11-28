import random
from mayo_utils import Q
from mayo_primitives import MAYO_Simulator

# --- 1. DEFAULT PARAMETERS ---
DEFAULT_M = 4 # Number of equations (Hash size)
DEFAULT_N = 6 # Size of signature blocks
DEFAULT_K = 2 # Number of signature blocks (Max 2 for this sim)

# --- 2. RANDOM PARAMETER GENERATION (Helper function) ---

def generate_random_matrix(rows, cols, modulus):
    """Generates a matrix with random elements in [0, modulus-1]."""
    return [[random.randint(0, modulus - 1) for _ in range(cols)] for _ in range(rows)]

def generate_random_matrices_and_signature(Q, M, N, K, sig_len):
    """Generates random public key matrices (P, E) and a random signature (S)."""
    # P_coeffs: M matrices of size N x N.
    P_coeffs = [generate_random_matrix(N, N, Q) for _ in range(M)]

    # E_matrices: M x M whipping transformation matrices. (Simplified for K=2)
    E_matrices = {
        "1,1": generate_random_matrix(M, M, Q),
        "2,2": generate_random_matrix(M, M, Q),
        # E_ij where i != j (assuming K=2 for the simulator)
        "1,2": generate_random_matrix(M, M, Q), 
    }
    
    # S_INPUT: Random signature vector of length N*K
    S_INPUT = [random.randint(0, Q - 1) for _ in range(sig_len)]
    
    return P_coeffs, E_matrices, S_INPUT

def generate_mayo_test_parameters(M, N, K, force_valid):
    """
    Generates all test parameters.
    If force_valid is True, T_PRIME_HASH_INPUT is set to P*(S_INPUT), guaranteeing success.
    """
    SIG_LENGTH = N * K
    
    # Always generate random public key and signature
    P_coeffs, E_matrices, S_INPUT = generate_random_matrices_and_signature(Q, M, N, K, SIG_LENGTH)

    if force_valid:
        # Guarantee VALID: Calculate the expected output T = P*(S)
        temp_simulator = MAYO_Simulator(P_coeffs, E_matrices, M, N, K)
        T_PRIME_HASH_INPUT = temp_simulator.P_star_eval(S_INPUT, SIG_LENGTH)
    else:
        # Generate random hash T' independently (likely INVALID)
        T_PRIME_HASH_INPUT = [random.randint(0, Q - 1) for _ in range(M)]

    return P_coeffs, E_matrices, S_INPUT, T_PRIME_HASH_INPUT