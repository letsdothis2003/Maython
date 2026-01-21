import tkinter as tk
from tkinter import font, messagebox, ttk
import random
import string

from mayo_utils import DEFAULT_M, DEFAULT_N, DEFAULT_K, DEFAULT_O
from mayo_primitives import MAYO_Simulator
from mayo_data_setup import generate_mayo_test_parameters
from mayo_mainalg import run_detailed_verification, MAYO_PRESETS, get_nist_preset
import mayo_info
import mayo_password
#This runs main graphical interface for MAYTHON(most of the visual and organizational stuff). 
class MayoGuiApp:
    def __init__(self, master):
        self.master = master
        master.title("MAYTHON - Mayo  Simulator")
        master.config(bg='white')
        master.geometry("1000x1000")

        self.big_font = font.Font(family="Inter", size=18, weight="bold")
        self.medium_font = font.Font(family="Inter", size=12)
        self.mono_font = font.Font(family="Courier", size=10)
        
        self.preset_var = tk.StringVar(value="Custom")
        self.M_var = tk.StringVar(value=str(DEFAULT_M))
        self.N_var = tk.StringVar(value=str(DEFAULT_N))
        self.K_var = tk.StringVar(value=str(DEFAULT_K))
        self.O_var = tk.StringVar(value=str(DEFAULT_O))

        self.setup_main_layout()

    def setup_main_layout(self):
        # Sidebar Navigation
        self.nav_frame = tk.Frame(self.master, bg='black', width=220)
        self.nav_frame.pack(side=tk.LEFT, fill='y')
        self.nav_frame.pack_propagate(False)

        # Header in sidebar
        tk.Label(self.nav_frame, text="MAYTHON", font=self.big_font, bg='black', fg='white', pady=20).pack()

        nav_buttons = [
            ("Home", self.show_welcome_mode),
            ("Test it out", self.show_test_mode),
            ("Key Generator", self.show_keygen_mode),
            ("Information", self.show_info_mode)
        ]

        for text, cmd in nav_buttons:
            tk.Button(self.nav_frame, text=text, command=cmd, font=self.medium_font, 
                      bg='blue', fg='white', relief='flat', pady=10).pack(fill='x', padx=10, pady=5)

        self.content_frame = tk.Frame(self.master, bg='white')
        self.content_frame.pack(side=tk.RIGHT, fill='both', expand=True)
        self.show_welcome_mode()

    def update_presets(self, *args):
        selection = self.preset_var.get()
        data = get_nist_preset(selection)
        self.M_var.set(str(data["m"]))
        self.N_var.set(str(data["n"]))
        self.K_var.set(str(data["k"]))
        self.O_var.set(str(data["o"]))
        state = 'normal' if selection == "Custom" else 'disabled'
        for entry in self.entry_widgets: entry.config(state=state)

    def show_welcome_mode(self):
        self.clear_content()
        
        # Container for Title  
        header_frame = tk.Frame(self.content_frame, bg='white')
        header_frame.pack(pady=80)
        # Title 
        tk.Label(header_frame, text="Welcome to MAYTHON", font=self.big_font, bg='white', fg='black').pack(side=tk.LEFT)

        tk.Label(self.content_frame, text="MAYO is a post-quantum cryptography scheme. MAYTHON is a tool to discover what it is and how it works!", font=self.medium_font, bg='white', fg='black').pack()
        
        #Underline
        tk.Frame(self.content_frame, height=2, width=400, bg='black').pack(pady=20)  

    def show_info_mode(self):
        self.clear_content()
        mayo_info.show_info_view(self.content_frame, self.big_font, self.medium_font)

    def show_keygen_mode(self):
        self.clear_content()
        mayo_password.show_password_view(self.content_frame, self.big_font, self.medium_font, self.mono_font)

    def show_test_mode(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Lets test it", font=self.big_font, bg='white', fg='black', pady=10).pack()
        tk.Label(self.content_frame, text="Choose parameter set", font=self.medium_font, bg='white', fg='black').pack()

        preset_frame = tk.Frame(self.content_frame, bg='white')
        preset_frame.pack(pady=5)
        self.preset_dropdown = ttk.Combobox(preset_frame, textvariable=self.preset_var, values=list(MAYO_PRESETS.keys()), state="readonly")
        self.preset_dropdown.pack(side=tk.LEFT, padx=5)
        self.preset_dropdown.bind("<<ComboboxSelected>>", self.update_presets)

        param_frame = tk.Frame(self.content_frame, bg='white', padx=10, pady=10, relief='groove', bd=1)
        param_frame.pack(pady=10)
        
        self.entry_widgets = []
        labels = [("m:", self.M_var), ("n:", self.N_var), ("k:", self.K_var), ("o:", self.O_var)]
        for i, (l, v) in enumerate(labels):
            row, col = divmod(i, 2)
            tk.Label(param_frame, text=l, bg='white', fg='black').grid(row=row, column=col*2, padx=5)
            ent = tk.Entry(param_frame, textvariable=v, width=8, bg='white', fg='black')
            ent.grid(row=row, column=col*2+1, padx=5, pady=5)
            self.entry_widgets.append(ent)

        self.update_presets()
        tk.Button(self.content_frame, text="Run Verification", command=self.run_sim, bg='blue', fg='white', font=self.medium_font).pack(pady=10)
        
        self.log = tk.Text(self.content_frame, height=15, font=self.mono_font, bg='white', fg='black', padx=10, pady=10)
        self.log.pack(fill='both', expand=True, padx=20, pady=10)

    def run_sim(self):
        self.log.config(state='normal'); self.log.delete('1.0', tk.END); self.log.config(state='disabled')
        try:
            m, n, k, o = int(self.M_var.get()), int(self.N_var.get()), int(self.K_var.get()), int(self.O_var.get())
            P, E, S, T = generate_mayo_test_parameters(m, n, k, o)
            sim = MAYO_Simulator(P, E, m, n, k, o)
            run_detailed_verification(sim, S, T, self.append_step)
        except Exception as e: self.append_step(f"Error: {e}")

    def append_step(self, text):
        self.log.config(state='normal'); self.log.insert(tk.END, text + "\n"); self.log.see(tk.END); self.log.config(state='disabled')
        self.master.update_idletasks()

    def clear_content(self):
        for w in self.content_frame.winfo_children(): w.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = MayoGuiApp(root)
    root.mainloop()