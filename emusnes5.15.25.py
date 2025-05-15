import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time

class SNESEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("EMUSNESV0.1")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.bg_color = "#343434"
        self.accent_color = "#6D2D92"
        self.text_color = "#FFFFFF"
        self.button_color = "#565656"
        
        self.root.configure(bg=self.bg_color)
        
        self.current_rom = None
        self.is_running = False
        self.rect_id = None
        self.start_time = None
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.root.bind("<space>", self.toggle_emulation)
        self.root.bind("r", self.reset_emulation)
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM...", command=self.open_rom)
        file_menu.add_command(label="Recent ROMs", command=self.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        emulation_menu = tk.Menu(menubar, tearoff=0)
        emulation_menu.add_command(label="Start", command=self.start_emulation)
        emulation_menu.add_command(label="Pause", command=self.pause_emulation)
        emulation_menu.add_command(label="Reset", command=self.reset_emulation)
        menubar.add_cascade(label="Emulation", menu=emulation_menu)
        
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="Controller Settings", command=self.not_implemented)
        options_menu.add_command(label="Video Settings", command=self.not_implemented)
        options_menu.add_command(label="Audio Settings", command=self.not_implemented)
        menubar.add_cascade(label="Options", menu=options_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_frame(self):
        """Create the main display frame"""
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, width=600, height=340)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_frame.pack_propagate(False)
        
        self.rom_info_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.rom_info_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.rom_label = tk.Label(self.rom_info_frame, text="No ROM loaded", fg=self.text_color, bg=self.bg_color, font=("Arial", 10, "bold"))
        self.rom_label.pack(side=tk.LEFT)
        
        self.display_frame = tk.Frame(self.main_frame, bg="black", width=512, height=240)
        self.display_frame.pack(fill=tk.BOTH, expand=True)
        self.display_frame.pack_propagate(False)
        
        self.canvas = tk.Canvas(self.display_frame, bg="black", width=512, height=240)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_message("EMUSNESV0.1\nSelect File > Open ROM to load a SNES game")
        
        self.controls_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        button_style = {"bg": self.button_color, "fg": self.text_color, "width": 8, 
                        "relief": tk.RAISED, "padx": 5, "pady": 3, "borderwidth": 2}
        
        self.start_button = tk.Button(self.controls_frame, text="Start", command=self.start_emulation, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        self.start_button.bind("<Enter>", lambda e: self.status_label.config(text="Start emulation"))
        self.start_button.bind("<Leave>", lambda e: self.status_label.config(text=""))
        
        self.pause_button = tk.Button(self.controls_frame, text="Pause", command=self.pause_emulation, **button_style)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.bind("<Enter>", lambda e: self.status_label.config(text="Pause emulation"))
        self.pause_button.bind("<Leave>", lambda e: self.status_label.config(text=""))
        
        self.reset_button = tk.Button(self.controls_frame, text="Reset", command=self.reset_emulation, **button_style)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.bind("<Enter>", lambda e: self.status_label.config(text="Reset emulation"))
        self.reset_button.bind("<Leave>", lambda e: self.status_label.config(text=""))
        
        self.speed_label = tk.Label(self.controls_frame, text="Speed:", bg=self.bg_color, fg=self.text_color)
        self.speed_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.speed_var = tk.StringVar(value="1.0x")
        speed_options = ["0.5x", "0.75x", "1.0x", "1.5x", "2.0x"]
        self.speed_menu = ttk.Combobox(self.controls_frame, textvariable=self.speed_var, values=speed_options, width=5, state="readonly")
        self.speed_menu.pack(side=tk.LEFT)
        
        self.time_label = tk.Label(self.controls_frame, text="Time: 0.0s", bg=self.bg_color, fg=self.text_color)
        self.time_label.pack(side=tk.RIGHT, padx=(20, 0))
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Frame(self.root, bg=self.accent_color, height=20)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", bg=self.accent_color, fg=self.text_color, anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.fps_label = tk.Label(self.status_bar, text="FPS: --", bg=self.accent_color, fg=self.text_color, padx=5)
        self.fps_label.pack(side=tk.RIGHT)
    
    def draw_message(self, text):
        """Draw multi-line text on the canvas with a 'message' tag"""
        self.canvas.delete("message")
        lines = text.split('\n')
        y = 100
        for i, line in enumerate(lines):
            self.canvas.create_text(
                256, y + i * 30,
                text=line,
                fill="white",
                font=("Arial", 12),
                tags="message"
            )
    
    def open_rom(self):
        """Open a ROM file"""
        filetypes = [
            ("SNES ROM files", "*.sfc *.smc"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select SNES ROM",
            filetypes=filetypes
        )
        
        if filename and os.path.isfile(filename):
            self.current_rom = filename
            rom_name = os.path.basename(filename)
            self.rom_label.config(text=f"ROM: {rom_name}")
            self.status_label.config(text=f"Loaded: {rom_name}")
            self.is_running = False
            if self.rect_id is not None:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            self.canvas.delete("all")
            self.draw_message(f"ROM loaded: {rom_name}\nPress Start to begin emulation")
        else:
            messagebox.showerror("Error", "Invalid file selected.")
    
    def start_emulation(self):
        """Start emulation with animation"""
        if not self.current_rom:
            messagebox.showinfo("No ROM", "Please open a ROM file first.")
            return
        
        self.canvas.delete("message")
        
        if self.rect_id is None:
            self.canvas.create_rectangle(0, 200, 512, 240, fill="green")  # Ground
            self.rect_x = 0.0
            self.rect_y = 180.0
            self.rect_vx = 5.0
            self.rect_vy = -10.0  # Initial upward velocity
            self.gravity = 0.5
            self.rect_id = self.canvas.create_rectangle(
                self.rect_x, self.rect_y,
                self.rect_x + 20, self.rect_y + 20,
                fill="red"
            )
        
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.animate()
            self.update_time()
        
        self.status_label.config(text=f"Running: {os.path.basename(self.current_rom)}")
        self.fps_label.config(text="FPS: 60")
    
    def animate(self):
        """Animation loop running at ~60 FPS"""
        if self.is_running:
            speed = float(self.speed_var.get().replace('x', ''))
            self.rect_vy += self.gravity * speed  # Apply gravity
            self.rect_x += self.rect_vx * speed
            self.rect_y += self.rect_vy * speed
            
            # Bounce off horizontal walls
            if self.rect_x < 0 or self.rect_x > 512 - 20:
                self.rect_vx = -self.rect_vx
            
            # Bounce off the ground
            if self.rect_y > 200 - 20:  # 200 is the ground y-position
                self.rect_y = 200 - 20
                self.rect_vy = -self.rect_vy * 0.8  # Lose some energy on bounce
            
            self.canvas.coords(
                self.rect_id,
                int(self.rect_x), int(self.rect_y),
                int(self.rect_x) + 20, int(self.rect_y) + 20
            )
            
            self.root.after(16, self.animate)
    
    def update_time(self):
        """Update the time elapsed display"""
        if self.is_running:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Time: {elapsed:.1f}s")
            self.root.after(100, self.update_time)
    
    def pause_emulation(self):
        """Pause emulation"""
        if not self.current_rom:
            return
        
        if self.is_running:
            self.is_running = False
            self.draw_message("Emulation paused\nPress Start to resume")
            self.status_label.config(text=f"Paused: {os.path.basename(self.current_rom)}")
            self.fps_label.config(text="FPS: --")
    
    def reset_emulation(self, event=None):
        """Reset emulation"""
        if not self.current_rom:
            return
        
        self.is_running = False
        if self.rect_id is not None:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        self.canvas.delete("all")
        rom_name = os.path.basename(self.current_rom)
        self.draw_message(f"ROM loaded: {rom_name}\nPress Start to begin emulation")
        self.status_label.config(text=f"Reset: {rom_name}")
        self.time_label.config(text="Time: 0.0s")
    
    def toggle_emulation(self, event):
        """Toggle between start and pause emulation"""
        if self.is_running:
            self.pause_emulation()
        else:
            self.start_emulation()
    
    def not_implemented(self):
        """Placeholder for features not implemented"""
        messagebox.showinfo("Not Implemented", "This feature is not implemented in this version.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """EMUSNESV0.1

A simple SNES emulator UI mockup created with Tkinter.
        
This is just a demonstration of the UI - it does not actually emulate SNES hardware or run games.

Developed as a demonstration of Tkinter capabilities."""
        messagebox.showinfo("About EMUSNESV0.1", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SNESEmulator(root)
    root.mainloop()
