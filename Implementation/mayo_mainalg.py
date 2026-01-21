from mayo_utils import array_to_string, vector_mod_q
from mayo_primitives import MAYO_Simulator

# MAYO has a few parameter sets based on NIST testing, we wanted to replicate that along with allowing user to test with their own parameters. 
MAYO_PRESETS = {
    "Custom": {"m": 4, "n": 6, "k": 2, "o": 3},
    "MAYO-1": {"m": 60, "n": 66, "k": 9, "o": 8},
    "MAYO-2": {"m": 64, "n": 78, "k": 4, "o": 18},
    "MAYO-3": {"m": 96, "n": 99, "k": 11, "o": 9},
    "MAYO-5": {"m": 128, "n": 133, "k": 12, "o": 11}
}


#By the way, we've noticed that as you go with higher NIST parameter sets, MAYTHON runs a bit slower due to the increased complexity of the operations. Could also 
#just be our machines and how python operates versus C(which the original creators of MAYO used cause it was more efficient for hardware). Keep that in mind
def get_nist_preset(name):
    """Returns the parameter dictionary for a given NIST preset name."""
    return MAYO_PRESETS.get(name, MAYO_PRESETS["Custom"])

def run_detailed_verification(simulator, s, t_target, append_callback):
    """
    Executes an optimized, step-by-step breakdown of the MAYO verification process.
    """
    q = 256  
    m = simulator.m 
    n = simulator.n 
    k = simulator.k 
    o = simulator.o 
    total_vars = n * k
    
    append_callback("THE ALICE & BOB SCENARIO")
    append_callback(f"Field Size (q): {q}")
    append_callback(f"Signature Blocks (k): {k}")
    append_callback(f"Variables per Block (n): {n}")
    append_callback(f"Total Signature Length: {total_vars}")
    append_callback(f"Number of Equations (m): {m}")
    append_callback(f"Secret Oil Space (o): {o}")
    append_callback("")
    append_callback("1. KEY GEN: Alice(reciever) created a secret 'Trapdoor' (o) and published her 'Public Lock'.")
    append_callback("2. SIGNING: Alice used her Trapdoor (o) to solve the quadratic system.")
    append_callback("3. VERIFICATION: Bob(recipient) uses the 'Public Lock' (Whipped Map P*) to check the signature.")
    append_callback("")

    
    append_callback(f"Target Hash (t): {array_to_string(t_target[:8])}{'...' if m > 8 else ''}")
    append_callback(f"Signature (s):   {array_to_string(s[:8])}{'...' if total_vars > 8 else ''}")
    append_callback("")

    # STEP 1: Un-shuffling
    append_callback("STEP 1: UN-SHUFFLING THE SIGNATURE")
    append_callback(f"Bob splits the signature 's' into {k} blocks of size {n}.")
    s_blocks = [s[i*n : (i+1)*n] for i in range(k)]
    for i, block in enumerate(s_blocks):
        if i < 3: # Only show first 3 blocks to keep log clean
            append_callback(f"Block s_{i+1}: {array_to_string(block[:6])}{'...' if n > 6 else ''}")
    if k > 3: append_callback(f"... and {k-3} more blocks.")
    append_callback("")

    # STEP 2: Evaluation
    append_callback("STEP 2: TESTING THE TRAPDOOR COMPONENTS")
    append_callback("Bob evaluates each block through the public quadratic maps (P).")
    p_evals = []
    for i in range(k):
        val = simulator.P_eval(s_blocks[i])
        p_evals.append(val)
        if i < 2:
            append_callback(f"Evaluation P(s_{i+1}): {array_to_string(val[:6])}{'...' if m > 6 else ''}")
    append_callback(f"Evaluated all {k} blocks.")
    append_callback("")

    # STEP 3: Interactions
    append_callback("STEP 3: ANALYZING BLOCK INTERACTIONS")
    append_callback("Bob calculates the Differential Maps P' to see how blocks interact.")
    p_primes = {}
    interaction_count = 0
    for i in range(k):
        for j in range(i + 1, k):
            val = simulator.P_prime(s_blocks[i], s_blocks[j])
            p_primes[f"{i+1},{j+1}"] = val
            interaction_count += 1
    
    append_callback(f"Calculated {interaction_count} block-to-block interaction maps.")
    append_callback("")

    # STEP 4: Whipping
    append_callback("STEP 4: THE WHIPPED PUBLIC LOCK (P*)")
    append_callback("Bob 'whips' the results together using the public coefficients (E).")
    
    p_star_result = [0] * m

    # Optimized whipping loop
    for i in range(k):
        # Diagonal
        e_ii = simulator.E_matrices[f"{i+1},{i+1}"]
        p_val = p_evals[i]
        for r in range(m):
            row_sum = 0
            e_row = e_ii[r]
            for c in range(m):
                row_sum += e_row[c] * p_val[c]
            p_star_result[r] = (p_star_result[r] + row_sum) % q

    for i in range(k):
        for j in range(i + 1, k):
            # Interactions
            e_ij = simulator.E_matrices.get(f"{i+1},{j+1}")
            if e_ij:
                p_p_val = p_primes[f"{i+1},{j+1}"]
                for r in range(m):
                    row_sum = 0
                    e_row = e_ij[r]
                    for c in range(m):
                        row_sum += e_row[c] * p_p_val[c]
                    p_star_result[r] = (p_star_result[r] + row_sum) % q
    
    append_callback("Whipping complete. All quadratic and bilinear terms combined.")
    append_callback("")

    # FINAL STEP: Verdict and Verification
    append_callback("FINAL STEP: BOB'S JUDGEMENT(Verification)")
    append_callback(f"Calculated Output P*(s): {array_to_string(p_star_result[:8])}{'...' if m > 8 else ''}")
    append_callback(f"Expected Target Hash t: {array_to_string(t_target[:8])}{'...' if m > 8 else ''}")
    
    is_valid = (p_star_result == t_target)
    
    if is_valid:
        append_callback("\n[VERIFICATION SUCCESS]")
        append_callback("The calculated output P*(s) matches the target hash t exactly.")
        append_callback("Bob confirms the signature opens the lock!")
    else:
        append_callback("\n[VERIFICATION FAILURE]")
        append_callback("The calculated output P*(s) does NOT match the target hash t.")
        append_callback("The signature is invalid. The lock remains closed.")

    return is_valid, p_star_result