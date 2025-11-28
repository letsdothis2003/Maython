import tkinter as tk
from tkinter import font, messagebox
import random

# Import core components from other modules
from mayo_utils import Q, array_to_string
from mayo_primitives import MAYO_Simulator
from mayo_data_setup import DEFAULT_M, DEFAULT_N, DEFAULT_K, generate_mayo_test_parameters

class MayoGuiApp:
    def __init__(self, master):
        self.master = master
        master.title("MAYTHON(Mayo multivariete scheme simulator using python)")
        master.config(bg='#f7f9fb')
        master.geometry("850x750")

        # Define styles
        self.big_font = font.Font(family="Inter", size=18, weight="bold")
        self.medium_font = font.Font(family="Inter", size=12)
        self.mono_font = font.Font(family="Courier", size=10)
        
        # State variables for parameters
        self.M_var = tk.StringVar(value=str(DEFAULT_M))
        self.N_var = tk.StringVar(value=str(DEFAULT_N))
        self.K_var = tk.StringVar(value=str(DEFAULT_K))
        self.force_valid_var = tk.BooleanVar(value=True) 

        self.simulator = None
        self.S_INPUT = []
        self.T_PRIME_HASH_INPUT = []
        self.step_counter = 0

        self.setup_ui()

    def setup_ui(self):
        # --- Header Frame ---
        header_frame = tk.Frame(self.master, bg='grey')
        header_frame.pack(pady=15)
        
        tk.Label(header_frame, text="MAYTHON", font=self.big_font, bg='white', fg='black').pack()
        tk.Label(header_frame, text="Simulating the core P*(s) verification map (Q=256 Field).", font=self.medium_font, bg='#f7f9fb', fg='#4b5563').pack()
        
        # --- Parameter Inputs Frame ---
        param_frame = tk.Frame(self.master, bg='#eef2f6', padx=20, pady=10, relief='groove', bd=1)
        param_frame.pack(pady=10)
        
        # Parameter Labels and Entries
        tk.Label(param_frame, text="M (Hash/Output Size):", bg='#eef2f6', font=self.medium_font).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(param_frame, textvariable=self.M_var, width=5, font=self.medium_font).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(param_frame, text="N (Block Size):", bg='#eef2f6', font=self.medium_font).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(param_frame, textvariable=self.N_var, width=5, font=self.medium_font).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(param_frame, text="K (Number of Blocks - Max 2 in this Sim):", bg='#eef2f6', font=self.medium_font).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(param_frame, textvariable=self.K_var, width=5, font=self.medium_font).grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(param_frame, text=f"Q (Field Size): {Q}", bg='#eef2f6', font=self.medium_font, fg='#4b5563').grid(row=0, column=2, padx=15, pady=5, sticky='w', rowspan=3)

        # Randomize Button
        tk.Button(param_frame, text="Randomize M, N, K", command=self.randomize_params, font=self.medium_font, bg='#dbeafe', fg='#1e40af', relief='raised').grid(row=3, column=0, columnspan=2, pady=10)


        # --- Controls and Run Frame ---
        controls_frame = tk.Frame(self.master, bg='#f7f9fb', padx=50)
        controls_frame.pack(pady=10)
        
        tk.Checkbutton(
            controls_frame, 
            text="Force Valid Signature (Guaranteed Success)", 
            variable=self.force_valid_var, 
            font=self.medium_font, 
            bg='#f7f9fb', 
            fg='#1f2937',
            selectcolor='#eef2f6'
        ).pack(side=tk.LEFT, padx=10)

        self.run_button = tk.Button(controls_frame, text="Run Verification", command=self.start_simulation, font=self.big_font, bg='#2563eb', fg='white', relief='raised', padx=20, pady=10, activebackground='#3b82f6')
        self.run_button.pack(side=tk.RIGHT, padx=10)


        # --- Result Card (Hidden initially) ---
        self.result_frame = tk.Frame(self.master, bg='#ffffff', bd=2, relief='flat', padx=20, pady=10, highlightbackground="#cccccc", highlightthickness=1)
        self.result_frame.pack(pady=10, fill='x', padx=50)
        self.result_frame.pack_forget()

        self.result_label = tk.Label(self.result_frame, text="", font=self.big_font, bg='#ffffff', fg='#10b981')
        self.result_label.pack()

        # --- Simulation Steps Container ---
        text_frame = tk.Frame(self.master, padx=50, pady=10)
        text_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.steps_text = tk.Text(text_frame, height=15, width=80, font=self.medium_font, bd=0, padx=10, pady=10, state=tk.DISABLED, wrap=tk.WORD, bg='#eef2f6', yscrollcommand=scrollbar.set)
        self.steps_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.steps_text.yview)

    def randomize_params(self):
        """Sets M, N, K to small random values for demonstration."""
        # Use small bounds to keep simulation fast and output readable
        self.M_var.set(str(random.randint(3, 8)))
        self.N_var.set(str(random.randint(5, 12)))
        self.K_var.set(str(2)) # Keep K=2 for the current P* map simulation

    def validate_and_get_params(self):
        """Reads and validates user input parameters."""
        try:
            M = int(self.M_var.get())
            N = int(self.N_var.get())
            K = int(self.K_var.get())
            
            if M < 2 or N < 2 or K < 2:
                raise ValueError("M, N, and K must be integers greater than 1.")
            if K > 2:
                # The simulator logic for E_matrices is simplified for K=2 in mayo_primitives
                raise ValueError("This simulator currently only supports K=2 blocks.")

            return M, N, K
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid integers for parameters. Error: {e}")
            return None

    def append_step(self, title, content, character_action="", is_running=False, is_success=None):
        """
        Appends text to the steps log with formatting.
        
        Args:
            title (str): The title of the step.
            content (str): The main content/results.
            character_action (str): The persona narrative.
            is_running (bool): True if the step is currently executing.
            is_success (bool/None): If the step is complete, indicates success/failure.
        """
        self.steps_text.config(state=tk.NORMAL)
        
        # Determine step indicator and color based on status
        if is_running:
            indicator = ' ● '
            title_fg = 'blue' # Blue for running
        elif is_success is True:
            indicator = ' ✓ '
            title_fg= 'green' # Green for success
        elif is_success is False:
            # Change indicator to 'X' and color to Red for failed step
            indicator = ' X ' 
            title_fg = 'red' # Red for failure
        else: # Default for completed intermediate steps
            indicator = ' ✓ ' 
            title_fg = 'green'

        self.steps_text.insert(tk.END, f"\n{indicator} STEP {self.step_counter}: {title}\n", 'title')
        
        # Insert Character Action
        self.steps_text.insert(tk.END, f"{character_action}\n", 'character_action') 
        
        self.steps_text.insert(tk.END, content + "\n\n", 'content')
        
        # Tag configuration (for colors/fonts)
        self.steps_text.tag_config('title', font=self.big_font, foreground=title_fg, justify='left', lmargin1=5, lmargin2=5)
        self.steps_text.tag_config('character_action', font=self.medium_font, foreground='#4b5563', lmargin1=5, lmargin2=5, spacing1=5) # New tag
        self.steps_text.tag_config('content', font=self.mono_font, foreground='#1f2937', lmargin1=15, lmargin2=15)

        self.steps_text.see(tk.END)
        self.steps_text.config(state=tk.DISABLED)
        self.master.update_idletasks()

    def start_simulation(self):
        """Initializes and starts the step-by-step simulation with current parameters."""
        params = self.validate_and_get_params()
        if not params:
            return

        M, N, K = params
        
        self.run_button.config(state=tk.DISABLED, text="Generating New Parameters...")
        
        # Clear log and hide results
        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete('1.0', tk.END)
        self.steps_text.config(state=tk.DISABLED)
        self.result_frame.pack_forget()
        self.step_counter = 0
        
        # --- NEW RANDOMIZATION ---
        force_valid = self.force_valid_var.get()
        P_coeffs, E_matrices, self.S_INPUT, self.T_PRIME_HASH_INPUT = generate_mayo_test_parameters(
            M, N, K, force_valid
        )
        self.simulator = MAYO_Simulator(P_coeffs, E_matrices, M, N, K)
        SIG_LENGTH = N * K
        # --- END NEW RANDOMIZATION ---

        self.run_button.config(text="Running...")
        # Start the sequence of steps
        self.master.after(500, self.step1_setup, M, N, K, SIG_LENGTH)

    def step1_setup(self, M, N, K, SIG_LENGTH):
        self.step_counter = 1
        title = 'Initial Setup: Load Public Key and Signature'
        s_str = array_to_string(self.S_INPUT)
        t_str = array_to_string(self.T_PRIME_HASH_INPUT)
        
        s1_len = len(self.S_INPUT[:N])
        s2_len = len(self.S_INPUT[N:])
        
        character_action = "👤 Alice (The Signer) sends Bob the Public Key (P, E matrices), the Signature (s), and the Target Hash (t')."
        
        content = f"""
Public key matrices and inputs have been randomly generated (Q={Q}).

Current Parameters: M={M}, N={N}, K={K}.
Total Signature Length: {SIG_LENGTH} bytes

Signature (s): {s_str} 
Target Hash (t'): {t_str} 
    Output Dimension: {M} bytes

Signature is split into K={K} blocks:
    Block s1 (Size N): {s1_len} bytes
    Block s2 (Size N): {s2_len} bytes
"""
        self.append_step(title, content, character_action, is_running=True)
        self.master.after(1500, self.step2_peval)

    def step2_peval(self):
        self.step_counter = 2
        title = 'Evaluate Base Map P(x)'
        
        character_action = "🧑‍💻 Bob (The Verifier) begins calculating the quadratic parts of the verification map using the P matrices: P(s1) and P(s2)."
        
        self.append_step(title, "Calculating the quadratic map output for each signature block. This uses the core quadratic form: P(x)i = x^T * Pi * x (mod Q).", character_action, is_running=True)
        
        # Perform calculations
        N = self.simulator.N
        self.p_s1 = self.simulator.P_eval(self.S_INPUT[:N])
        self.p_s2 = self.simulator.P_eval(self.S_INPUT[N:])
        
        content = f"""
Result for Block 1 (Size M={self.simulator.M}):
P(s1): {array_to_string(self.p_s1)}

Result for Block 2 (Size M={self.simulator.M}):
P(s2): {array_to_string(self.p_s2)}
"""
        self.append_step(f'{title} (Results)', content, is_success=True)
        self.master.after(1500, self.step3_pprime)

    def step3_pprime(self):
        self.step_counter = 3
        title = "Calculate Differential Map P'(s1, s2)"
        
        character_action = "🧑‍💻 Bob calculates the bilinear cross-term between the signature blocks (s1 and s2)."
        
        self.append_step(title, "Formula: P'(s1, s2) = P(s1+s2) - P(s1) - P(s2) (mod Q).", character_action, is_running=True)
        
        # Perform calculation
        N = self.simulator.N
        self.p_prime_s1s2 = self.simulator.P_prime(self.S_INPUT[:N], self.S_INPUT[N:])
        
        content = f"""
P'(s1, s2) (Size M={self.simulator.M}): {array_to_string(self.p_prime_s1s2)}
"""
        self.append_step(f'{title} (Results)', content, is_success=True)
        self.master.after(1500, self.step4_pstar)

    def step4_pstar(self):
        self.step_counter = 4
        title = "Whipped Map P*(s) Evaluation"
        
        character_action = "🧑‍💻 Bob applies the E (whipping) matrices to the calculated terms to produce his verification hash (T)."
        
        self.append_step(title, "Formula: T = E11*P(s1) + E22*P(s2) + E12*P'(s1, s2) (mod Q).", character_action, is_running=True)
        
        # Recalculate terms (for display detail)
        # Note: P*(s) is recalculated fully inside P_star_eval, but we use the stored P(s) and P'(s) terms for the step output.
        self.T_CALCULATED = self.simulator.P_star_eval(self.S_INPUT, self.simulator.N * self.simulator.K)
        
        # To show the intermediate steps, we manually calculate the terms again (redundant but illustrative)
        E11 = self.simulator.E_matrices["1,1"]
        E22 = self.simulator.E_matrices["2,2"]
        E12 = self.simulator.E_matrices["1,2"]
        M = self.simulator.M
        
        # We assume the simulator has access to the utility functions via imports in mayo_primitives
        # but since we are in the main GUI file, we use the explicit imports
        from mayo_utils import dot_product, vector_mod_q 
        
        term_A = vector_mod_q(dot_product(E11, self.p_s1))
        term_B = vector_mod_q(dot_product(E22, self.p_s2))
        term_C = vector_mod_q(dot_product(E12, self.p_prime_s1s2))


        content = f"""
Term A (E11 * P(s1)): {array_to_string(term_A)}
Term B (E22 * P(s2)): {array_to_string(term_B)}
Term C (E12 * P'(s1, s2)): {array_to_string(term_C)}

Calculated Output T = P*(s): {array_to_string(self.T_CALCULATED)}
"""
        self.append_step(f'{title} (Results)', content, is_success=True)
        self.master.after(1500, self.step5_compare)

    def step5_compare(self):
        self.step_counter = 5
        title = "Final Comparison"
        
        character_action = "🧑‍💻 Bob compares his calculated hash (T) with Alice's target hash (T') to verify the signature."
        
        # CRITICAL: This comparison check determines the outcome.
        is_valid = self.T_CALCULATED == self.T_PRIME_HASH_INPUT

        # Update Result Card appearance
        self.result_frame.pack(pady=10, fill='x', padx=50)

        # Display result based ONLY on the comparison of the two arrays.
        if is_valid:
            # Green for success
            result_text = f"VERIFICATION PASS"
            fg_color = 'blue' # Deeper green for text
            bg_color = 'blue' # Light green background
        else:
            # Red for failure
            result_text = f"VERIFICATION FAILED"
            fg_color = 'red' # Deep red for text
            bg_color = 'blue' # Light red background

        self.result_frame.config(bg=bg_color)
        self.result_label.config(text=result_text, fg=fg_color, bg=bg_color)

        content = f"""
Calculated Output T (P*(s)): {array_to_string(self.T_CALCULATED)}
Target Hash T' (Hash of message): {array_to_string(self.T_PRIME_HASH_INPUT)}
"""
        # Append step, using the is_valid result to color the step title itself
        self.append_step(f'{title} (Results)', content, character_action, is_success=is_valid)
        
        # Final button state
        self.run_button.config(state=tk.NORMAL, text="Run Verification")

# The code below is required for the application to run when the Python file is executed.
if __name__ == '__main__':
    root = tk.Tk()
    # Setting Tk to be resizable by default for better embedding experience
    root.resizable(True, True) 
    app = MayoGuiApp(root)
    root.mainloop()