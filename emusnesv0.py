import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import random

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
        self.player_id = None
        self.obstacles = []
        self.start_time = None
        self.score = 0
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.root.bind("<space>", self.toggle_emulation)
        self.root.bind("r", self.reset_emulation)
        self.root.bind("<Left>", lambda e: self.move_player(-10))
        self.root.bind("<Right>", lambda e: self.move_player(10))
    
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
        
        self.score_label = tk.Label(self.controls_frame, text="Score: 0", bg=self.bg_color, fg=self.text_color)
        self.score_label.pack(side=tk.RIGHT, padx=(20, 0))
    
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
            self.reset_emulation()
        else:
            messagebox.showerror("Error", "Invalid file selected.")
    
    def start_emulation(self):
        """Start emulation with animation"""
        if not self.current_rom:
            messagebox.showinfo("No ROM", "Please open a ROM file first.")
            return
        
        self.canvas.delete("message")
        
        if self.player_id is None:
            self.create_game_scene()
        
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.animate()
            self.update_time()
            self.update_score()
        
        self.status_label.config(text=f"Running: {os.path.basename(self.current_rom)}")
        self.fps_label.config(text="FPS: 60")
    
    def create_game_scene(self):
        """Create a simple game scene with a player and obstacles"""
        self.canvas.delete("all")
        # Draw background tiles
        for i in range(0, 512, 32):
            for j in range(0, 240, 32):
                self.canvas.create_rectangle(i, j, i+32, j+32, fill="gray", outline="black")
        # Draw player
        self.player_x = 256
        self.player_y = 200
        self.player_id = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + 20, self.player_y + 20,
            fill="blue"
        )
        # Draw obstacles
        self.obstacles = []
        for _ in range(5):
            obs_x = random.randint(0, 492)
            obs_y = random.randint(0, 220)
            obs_id = self.canvas.create_oval(
                obs_x, obs_y,
                obs_x + 20, obs_y + 20,
                fill="red"
            )
            self.obstacles.append((obs_id, obs_x, obs_y))
    
    def animate(self):
        """Animation loop running at ~60 FPS"""
        if self.is_running:
            speed = float(self.speed_var.get().replace('x', ''))
            # Move obstacles
            for i, (obs_id, obs_x, obs_y) in enumerate(self.obstacles):
                obs_x += 2 * speed
                if obs_x > 512:
                    obs_x = -20
                self.canvas.coords(obs_id, obs_x, obs_y, obs_x + 20, obs_y + 20)
                self.obstacles[i] = (obs_id, obs_x, obs_y)
                # Check collision with player
                if (self.player_x < obs_x + 20 and self.player_x + 20 > obs_x and
                    self.player_y < obs_y + 20 and self.player_y + 20 > obs_y):
                    self.score += 1
                    self.canvas.delete(obs_id)
                    self.obstacles[i] = (None, None, None)
            # Remove collected obstacles
            self.obstacles = [obs for obs in self.obstacles if obs[0] is not None]
            # Add new obstacles
            if len(self.obstacles) < 5:
                obs_x = random.randint(0, 492)
                obs_y = random.randint(0, 220)
                obs_id = self.canvas.create_oval(
                    obs_x, obs_y,
                    obs_x + 20, obs_y + 20,
                    fill="red"
                )
                self.obstacles.append((obs_id, obs_x, obs_y))
            self.root.after(16, self.animate)
    
    def move_player(self, dx):
        """Move the player left or right"""
        if self.is_running:
            new_x = self.player_x + dx
            if 0 <= new_x <= 492:
                self.player_x = new_x
                self.canvas.coords(self.player_id, self.player_x, self.player_y,
                                   self.player_x + 20, self.player_y + 20)
    
    def update_time(self):
        """Update the time elapsed display"""
        if self.is_running:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Time: {elapsed:.1f}s")
            self.root.after(100, self.update_time)
    
    def update_score(self):
        """Update the score display"""
        if self.is_running:
            self.score_label.config(text=f"Score: {self.score}")
            self.root.after(100, self.update_score)
    
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
        self.is_running = False
        self.player_id = None
        self.obstacles = []
        self.score = 0
        self.canvas.delete("all")
        if self.current_rom:
            rom_name = os.path.basename(self.current_rom)
            self.draw_message(f"ROM loaded: {rom_name}\nPress Start to begin emulation")
            self.status_label.config(text=f"Reset: {rom_name}")
        else:
            self.draw_message("EMUSNESV0.1\nSelect File > Open ROM to load a SNES game")
            self.status_label.config(text="Ready")
        self.time_label.config(text="Time: 0.0s")
        self.score_label.config(text="Score: 0")
    
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
