from mayo_utils import Q, poly_eval_mod, dot_product, vector_mod_q

class MAYO_Simulator:
    def __init__(self, P_coeffs, E_matrices, M, N, K):
        self.P_coeffs = P_coeffs
        self.E_matrices = E_matrices
        self.M = M
        self.N = N
        self.K = K

    def P_eval(self, x):
        """Calculates P(x) = x^T * P_i * x for each P_i matrix (mod Q)"""
        result = [0] * self.M
        for i in range(self.M):
            P_i = self.P_coeffs[i]
            # 1. P_i * x (Matrix * Vector)
            Px = dot_product(P_i, x)
            # 2. x^T * (P_i * x) (Vector.T * Vector)
            p_i = dot_product(x, Px)
            result[i] = poly_eval_mod(p_i)
        return result

    def P_prime(self, x, y):
        """Calculates the differential map: P'(x, y) = P(x+y) - P(x) - P(y) (mod Q)"""
        x_plus_y = [x[i] + y[i] for i in range(len(x))]

        P_x_plus_y = self.P_eval(x_plus_y)
        P_x = self.P_eval(x)
        P_y = self.P_eval(y)

        # Modulo arithmetic applied during subtraction (a - b - c mod Q)
        result = [P_x_plus_y[i] - P_x[i] - P_y[i] for i in range(self.M)]

        return vector_mod_q(result)

    def P_star_eval(self, s, sig_len):
        """
        Calculates the Whipped Map: 
        P*(s) = SUM(E_ii * P(s_i)) + SUM(E_ij * P'(s_i, s_j)) (mod Q)
        """
        # Calculate block sizes based on current N and K
        s_blocks = [s[i*self.N:(i+1)*self.N] for i in range(self.K)]

        # Term 1: Quadratic terms (E_ii * P(s_i))
        quad_term = [0] * self.M
        for i in range(self.K):
            s_i = s_blocks[i]
            p_si = self.P_eval(s_i)
            e_ii = self.E_matrices[f"{i+1},{i+1}"]
            
            term = dot_product(e_ii, p_si)
            quad_term = [quad_term[idx] + term[idx] for idx in range(self.M)]

        # Term 2: Bilinear terms (E_ij * P'(s_i, s_j))
        bilinear_term = [0] * self.M
        
        # This simulator assumes K=2 for the E matrix logic (1,1, 2,2, 1,2)
        if self.K == 2:
            s_i = s_blocks[0]
            s_j = s_blocks[1]
            
            p_prime_ij = self.P_prime(s_i, s_j)
            e_ij = self.E_matrices["1,2"]
            
            term = dot_product(e_ij, p_prime_ij)
            bilinear_term = [bilinear_term[idx] + term[idx] for idx in range(self.M)]
        # NOTE: For K > 2, the E_matrices structure would require significant modification.

        # Final result: P*(s) = (quad_term + bilinear_term) mod Q
        result = [quad_term[i] + bilinear_term[i] for i in range(self.M)]
        return vector_mod_q(result)