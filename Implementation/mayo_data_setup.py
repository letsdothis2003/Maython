import random
from mayo_utils import Q

def generate_mayo_test_parameters(m, n, k, o, force_valid=True):
    """Generates all matrices and a test signature for simulation."""
    # 1. Generate m random n x n matrices for P
    P = []
    for _ in range(m):
        mat = [[random.randint(0, Q-1) for _ in range(n)] for _ in range(n)]
        P.append(mat)

    # 2. Generate E matrices for all pairs (i,j) where i <= j <= k
    E = {}
    for i in range(1, k + 1):
        for j in range(i, k + 1):
            # Identity-like diagonal for demo, random off-diagonal
            mat = [[0]*m for _ in range(m)]
            for r in range(m):
                mat[r][r] = 1 if i == j else random.randint(0, Q-1)
            E[f"{i},{j}"] = mat

    # 3. Generate a signature (k blocks of size n)
    s_full = [random.randint(0, Q-1) for _ in range(n * k)]
    s_blocks = [s_full[i*n : (i+1)*n] for i in range(k)]

    # 4. Generate Target
    if force_valid:
        # To ensure success, calculate what T would be for this S
        from mayo_primitives import MAYO_Simulator
        sim = MAYO_Simulator(P, E, m, n, k, o)
        t_target = sim.P_star_eval(s_blocks)
    else:
        t_target = [random.randint(0, Q-1) for _ in range(m)]

    return P, E, s_full, t_target