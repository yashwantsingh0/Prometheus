# gui/interface.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform

class PrometheusApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Prometheus - File Compressor")
        self.root.geometry("900x600")
        self.root.minsize(700, 500)
        self.theme = "light"

        self.setup_style()
        self.build_menu()
        self.build_main_ui()

    def setup_style(self):
        # Apply ttk theme based on OS
        style = ttk.Style(self.root)
        if platform.system() == "Darwin":
            style.theme_use("aqua")
        elif platform.system() == "Windows":
            style.theme_use("vista")
        else:
            style.theme_use("clam")

    def build_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Files", command=self.open_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Theme Toggle
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="Theme", menu=theme_menu)

        # About
        menubar.add_command(label="About", command=self.show_about)

        self.root.config(menu=menubar)

    def build_main_ui(self):
        self.drop_area = tk.Label(
            self.root,
            text="Drag & Drop Files Here or Use File Menu",
            relief="groove",
            bd=2,
            padx=10,
            pady=30,
            bg="#f0f0f0",
            font=("Arial", 14),
        )
        self.drop_area.pack(fill="both", expand=True, padx=20, pady=20)

    def open_files(self):
        filetypes = [
            ("Supported files", "*.jpg *.jpeg *.png *.pdf"),
            ("All files", "*.*"),
        ]
        files = filedialog.askopenfilenames(
            title="Select files", filetypes=filetypes
        )
        if files:
            # Placeholder for now
            print("Selected files:", files)

    def toggle_theme(self):
        # Placeholder: theme switching logic will go in theme.py later
        if self.theme == "light":
            self.theme = "dark"
            self.drop_area.config(bg="#2c2c2c", fg="white")
        else:
            self.theme = "light"
            self.drop_area.config(bg="#f0f0f0", fg="black")

    def show_about(self):
        messagebox.showinfo(
            "About Prometheus",
            "Prometheus File Compressor\nDeveloped by Yashwant\nSupports JPG, PNG, PDF compression with full control.",
        )

    def run(self):
        self.root.mainloop()
