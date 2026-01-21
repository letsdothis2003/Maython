from mayo_utils import vector_mod_q

class MAYO_Simulator:
    def __init__(self, P_matrices, E_matrices, m, n, k, o):
        """
        P_matrices: List of m matrices (n x n)
        E_matrices: Dictionary of (i,j) -> (m x m) whipping matrices
        """
        self.P = P_matrices
        self.E_matrices = E_matrices
        self.m = m
        self.n = n
        self.k = k
        self.o = o

    def P_eval(self, x):
        """Evaluates the public quadratic map P on a vector x of length n."""
        res = []
        for i in range(self.m):
            val = 0
            mat = self.P[i]
            for r in range(self.n):
                for c in range(self.n):
                    val += mat[r][c] * x[r] * x[c]
            res.append(val % 256)
        return res

    def P_prime(self, x, y):
        """Differential map P'(x,y) = P(x+y) - P(x) - P(y)."""
        res = []
        for i in range(self.m):
            val = 0
            mat = self.P[i]
            for r in range(self.n):
                for c in range(self.n):
                    val += mat[r][c] * (x[r] * y[c] + x[c] * y[r])
            res.append(val % 256)
        return res

    def P_star_eval(self, s_blocks):
        """Computes the whipped P* evaluation over k blocks."""
        m_dim = self.m
        total_res = [0] * m_dim
        
        # Diagonal terms: E_ii * P(s_i)
        for i in range(self.k):
            p_val = self.P_eval(s_blocks[i])
            e_ii = self.E_matrices[f"{i+1},{i+1}"]
            term = [sum(e_ii[r][c] * p_val[c] for c in range(m_dim)) % 256 for r in range(m_dim)]
            total_res = [(total_res[idx] + term[idx]) % 256 for idx in range(m_dim)]

        # Off-diagonal terms: E_ij * P'(s_i, s_j)
        for i in range(self.k):
            for j in range(i + 1, self.k):
                p_prime_val = self.P_prime(s_blocks[i], s_blocks[j])
                e_ij = self.E_matrices[f"{i+1},{j+1}"]
                term = [sum(e_ij[r][c] * p_prime_val[c] for c in range(m_dim)) % 256 for r in range(m_dim)]
                total_res = [(total_res[idx] + term[idx]) % 256 for idx in range(m_dim)]
        
        return total_res