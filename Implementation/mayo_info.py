import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import os

# Note: This requires 'pip install pymupdf' to function
try:
    import fitz 
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

def open_url(url):
    webbrowser.open_new(url)

def show_info_view(parent, big_font, medium_font):
    """Renders a scrollable view with a centered, resizable PDF document viewer."""
    
    # This is our main container 
    bg_color = 'white'
    main_canvas = tk.Canvas(parent, bg=bg_color, highlightthickness=0)
    main_v_scroll = tk.Scrollbar(parent, orient="vertical", command=main_canvas.yview)
    scrollable_frame = tk.Frame(main_canvas, bg=bg_color)

    def update_main_scrollregion(event=None):
        # Everything should be scrollable
        scrollable_frame.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", update_main_scrollregion)

    main_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    def sync_width(event):
        canvas_width = event.width
        main_canvas.itemconfig(main_window, width=canvas_width)
        
    main_canvas.bind("<Configure>", sync_width)

    main_canvas.pack(side="left", fill="both", expand=True)
    main_v_scroll.pack(side="right", fill="y")
    main_canvas.configure(yscrollcommand=main_v_scroll.set)

    # This is our header
    tk.Label(scrollable_frame, text="Information(and Documentation)", font=big_font, bg=bg_color, fg='black', pady=20).pack()

    # Our main way of showcasing information is making a viewing window with a pdf of our report
    # Changed bg='w' to 'white'
    paned_window = tk.PanedWindow(scrollable_frame, orient=tk.VERTICAL, bg='white', sashwidth=6, sashrelief='flat')
    paned_window.pack(fill='both', expand=True, padx=40, pady=(10, 30))

    # PDF Container
    pdf_container = tk.Frame(paned_window, bg='white', height=1200) 
    paned_window.add(pdf_container, minsize=600)

    # Links container with our sources 
    links_container = tk.Frame(paned_window, bg='white', pady=30)
    paned_window.add(links_container, minsize=450)

    #this should connect our pdf file into here 
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    project_root = os.path.dirname(current_dir) 
    pdf_path = os.path.join(project_root, "Documentation", "What_Is_Mayo.pdf")
    
    if not PDF_SUPPORT:
        tk.Label(pdf_container, text="PDF library (PyMuPDF) missing.\nRun: pip install pymupdf", 
                 bg='white', fg='red', font=medium_font).pack(expand=True)
    elif not os.path.exists(pdf_path):
        tk.Label(pdf_container, text=f"File not found at:\n{pdf_path}\n\nPlease ensure the 'Documentation' folder exists.", 
                 bg='white', fg='black', font=medium_font, justify='center').pack(expand=True)
    else:
        pdf_bg = 'white'
        pdf_canvas = tk.Canvas(pdf_container, bg=pdf_bg, highlightthickness=0)
        pdf_v_scroll = tk.Scrollbar(pdf_container, orient="vertical", command=pdf_canvas.yview)
        
        pdf_scroll_inner = tk.Frame(pdf_canvas, bg=pdf_bg)
        pdf_canvas_window = pdf_canvas.create_window((0, 0), window=pdf_scroll_inner, anchor="nw")
        pdf_canvas.configure(yscrollcommand=pdf_v_scroll.set)

        pdf_canvas.pack(side="left", fill="both", expand=True)
        pdf_v_scroll.pack(side="right", fill="y")

        try:
            doc = fitz.open(pdf_path)
            parent.pdf_images = [] 
            
            pages_stack = tk.Frame(pdf_scroll_inner, bg=pdf_bg)
            pages_stack.pack(expand=True, fill='both')
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0)) 
                img_data = pix.tobytes("ppm")
                tk_img = tk.PhotoImage(data=img_data)
                
                lbl = tk.Label(pages_stack, image=tk_img, bg=pdf_bg, pady=20, relief='flat')
                lbl.pack(anchor="center") 
                parent.pdf_images.append(tk_img)
            
            def center_pdf(event=None):
                pdf_scroll_inner.update_idletasks()
                pdf_canvas.config(scrollregion=pdf_canvas.bbox("all"))
                
                canvas_w = pdf_canvas.winfo_width()
                content_w = pdf_scroll_inner.winfo_reqwidth()
                
                if canvas_w > content_w:
                    new_x = (canvas_w - content_w) // 2
                    pdf_canvas.coords(pdf_canvas_window, new_x, 0)
                    pdf_canvas.itemconfig(pdf_canvas_window, width=content_w)
                else:
                    pdf_canvas.coords(pdf_canvas_window, 0, 0)
                    pdf_canvas.itemconfig(pdf_canvas_window, width=canvas_w)
                
                update_main_scrollregion()

            pdf_canvas.bind("<Configure>", center_pdf)
            pdf_scroll_inner.bind("<Configure>", center_pdf)
            
        except Exception as e:
            tk.Label(pdf_container, text=f"Error: {e}", bg='white').pack()

    # Our sources with links
    # Changed fg='#0f172a' to 'black' (dark slate)
    tk.Label(links_container, text="Our sources:", 
             font=("Arial", 12, "bold"), bg='white', fg='black').pack(anchor='w', padx=20, pady=(0, 10))

    links = [
        ("Official MAYO Website", "https://pqmayo.org/"),
        ("The Oil and Vinegar Method – William Buchanan", "https://www.researchgate.net/profile/William-Buchanan-3/publication/344396950_The_Oil_and_Vinegar_Method/links/5f7066c4a6fdcc00863f7e36/The-Oil-and-Vinegar-Method.pdf"),
        ("MAYO Presentation (NIST PQC Seminar, Sept 2024)", "https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/20-mayo-09242024.pdf"),
        ("MAYO Round 2 Specification Official Specs", "https://pqmayo.org/assets/specs/mayo-round2.pdf"),
        ("MAYO in Open Quantum Safe (liboqs) Algorithm Overview", "https://openquantumsafe.org/liboqs/algorithms/sig/mayo.html"),
        ("ACM Publication on Post-Quantum Signatures", "https://dl.acm.org/doi/pdf/10.1145/3658644.3690258"),
        ("MAYO: Practical Post-Quantum Signatures from Oil-and-Vinegar Maps – Ward Beullens", "https://cosicdatabase.esat.kuleuven.be/backend/publications/files/journal/3390"),
        ("SNOVA Specification Document – Round 2", "https://pqmayo.org/assets/specs/snova-round2.pdf"),
        ("HAWK v1.1 Specification Document – Round 2", "https://pqmayo.org/assets/specs/hawk-round2.pdf"),
        ("MAYO Parameter Timing Benchmarks Params & Timing Data", "https://pqmayo.org/params-times/"),
        ("MAYO Performance in CPU Cycles (AVX2 Optimizations)", "https://www.researchgate.net/figure/MAYO-performance-in-CPU-cycles-using-AVX2-optimizations-in-comparison-with-other_tbl2_378951120")
    ]

    for text, url in links:
        # Changed fg="#2563eb" to 'blue'
        link = tk.Label(links_container, text=f"• {text}", fg="blue", cursor="hand2", bg="white", font=medium_font)
        link.pack(anchor='w', pady=3, padx=40)
        link.bind("<Button-1>", lambda e, u=url: open_url(u))

    # Support for global mousewheel scrolling
    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", _on_mousewheel)