import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import string
import datetime

# Imports 
from mayo_utils import Q, array_to_string
from mayo_primitives import MAYO_Simulator
from mayo_data_setup import generate_mayo_test_parameters

def show_password_view(parent, big_font, medium_font, mono_font):
    """Modified MAYO tool: Stores encrypted passcodes directly to .txt files."""
    seed_var = tk.StringVar(value="default_system_seed")
    phrase_var = tk.StringVar()
    result_var = tk.StringVar(value="")
    decoded_var = tk.StringVar(value="********")
    is_revealed = False

    # bg='#f7f9fb' -> 'alice blue'
    tk.Label(parent, text="MAYO Secure Encryptor", font=big_font, bg='alice blue').pack(pady=10)

    # Configuration
    config_frame = tk.LabelFrame(parent, text=" Settings ", font=medium_font, bg='alice blue', padx=15, pady=10)
    config_frame.pack(fill='x', padx=20, pady=5)
    
    tk.Label(config_frame, text="System Seed:", bg='alice blue').grid(row=0, column=0, sticky='w')
    tk.Entry(config_frame, textvariable=seed_var, width=30).grid(row=0, column=1, padx=10, pady=5)
    
    def gen_random_seed():
        seed_var.set("".join(random.choices(string.ascii_letters + string.digits, k=12)))
    
    # bg='#64748b' -> 'slategray'
    tk.Button(config_frame, text="Random Seed", command=gen_random_seed, bg='slategray', fg='white', font=("Arial", 8)).grid(row=0, column=2)

    tk.Label(config_frame, text="Your Phrase:", bg='alice blue').grid(row=1, column=0, sticky='w')
    tk.Entry(config_frame, textvariable=phrase_var, font=medium_font, width=40).grid(row=1, column=1, columnspan=2, pady=5, sticky='w', padx=10)

    # Encryption & Integrity Check 
    def run_mayo_process():
        nonlocal is_revealed
        entropy = phrase_var.get()
        if not entropy:
            messagebox.showwarning("Input Needed", "Please enter a phrase to encrypt.")
            return

        is_revealed = False
        decoded_var.set("********")
        reveal_btn.config(text="Click to Reveal Phrase Source")

        m, n, k, o = 8, 6, 2, 3
        log_text.config(state='normal')
        log_text.delete('1.0', tk.END)
        
        def append_log(txt):
            log_text.insert(tk.END, txt + "\n")

        append_log("--- PROCESSING ENCRYPTION ---")
        
        state = random.getstate()
        random.seed(seed_var.get())
        append_log(f"[*] Constructing public map from seed...")
        P, E, _, _ = generate_mayo_test_parameters(m, n, k, o, force_valid=False)
        sim = MAYO_Simulator(P, E, m, n, k, o)
        
        random.seed(entropy)
        s_vector = [(ord(entropy[i % len(entropy)]) + (i * 13)) % Q for i in range(n * k)]
        s_blocks = [s_vector[i*n : (i+1)*n] for i in range(k)]
        append_log(f"[*] Mapping phrase to signature space...")
        
        final_hash = sim.P_star_eval(s_blocks)
        hex_output = "".join(f"{x:02x}" for x in final_hash).upper()
        formatted = "-".join([hex_output[i:i+4] for i in range(0, len(hex_output), 4)])
        result_var.set(formatted)
        append_log(f"[+] Encryption result: {formatted}")

        append_log("\n--- INTEGRITY VERIFICATION ---")
        check_hash = sim.P_star_eval(s_blocks)
        
        if check_hash == final_hash:
            append_log("[SUCCESS] Integrity passed. Code maps correctly to phrase vector.")
        else:
            append_log("[FAILED] Verification error detected.")
            
        log_text.config(state='disabled')
        random.setstate(state)

    def toggle_reveal():
        nonlocal is_revealed
        if not phrase_var.get(): return
        
        if not is_revealed:
            decoded_var.set(phrase_var.get())
            reveal_btn.config(text="Hide Phrase Source")
            is_revealed = True
        else:
            decoded_var.set("********")
            reveal_btn.config(text="Reveal Phrase Source")
            is_revealed = False

    # Modified Save Function: Exports directly to a .txt file
    def save_to_txt_file():
        code = result_var.get()
        phrase = phrase_var.get()
        if not code:
            messagebox.showwarning("Empty", "Generate a code first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            initialfile="encrypted_passcode.txt",
            title="Save Encrypted Passcode"
        )
        
        if path:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(path, "w") as f:
                    f.write("MAYO ENCRYPTED PASSCODE REPORT\n")
                    f.write("="*35 + "\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"Passcode:  {code}\n")
                    f.write("="*35 + "\n")
                messagebox.showinfo("Saved", f"Passcode successfully saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    # UI Widgets
    tk.Button(parent, text="Encrypt & Verify", command=run_mayo_process, 
              bg='royalblue', fg='white', font=medium_font, pady=8).pack(pady=10)

    # for logs
    log_frame = tk.Frame(parent, bg='alice blue', padx=20)
    log_frame.pack(fill='both', expand=True)
    log_text = tk.Text(log_frame, height=6, font=mono_font, bg='light gray')
    log_text.pack(fill='both', expand=True)
    log_text.config(state='disabled')

    # for reveal button
    reveal_frame = tk.Frame(parent, bg='whitesmoke', padx=10, pady=5, relief='sunken', bd=1)
    reveal_frame.pack(fill='x', padx=20, pady=5)
    tk.Label(reveal_frame, text="Decoded Phrase Source:", bg='whitesmoke', font=("Arial", 9, "bold")).pack(side=tk.LEFT)
    tk.Label(reveal_frame, textvariable=decoded_var, bg='whitesmoke', font=mono_font, fg='darkslategray').pack(side=tk.LEFT, padx=10)
    reveal_btn = tk.Button(reveal_frame, text="Reveal Phrase Source", command=toggle_reveal, font=("Arial", 8), bg='light grey')
    reveal_btn.pack(side=tk.RIGHT)

    # for frame
    footer = tk.Frame(parent, bg='midnight blue', pady=15)
    footer.pack(fill='x', side=tk.BOTTOM)
    
    # Result Display
    tk.Entry(footer, textvariable=result_var, font=mono_font, bg='midnight blue', 
              fg='wheat', relief='flat', justify='center', width=45, state='readonly').pack()
    
    btn_box = tk.Frame(footer, bg='midnight blue')
    btn_box.pack(pady=5)
    
    # Modified Button: Save to .txt
    tk.Button(btn_box, text="Save Passcode to .txt", command=save_to_txt_file, 
              bg='sea green', fg='white', font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, padx=5)