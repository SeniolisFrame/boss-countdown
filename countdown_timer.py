import os
import tkinter as tk
from tkinter import ttk, messagebox
import time

class CountdownRecord:
    def __init__(self, parent, level_group, channel, total_seconds):
        self.parent = parent
        self.level_group = level_group
        self.channel = channel
        self.start_seconds = total_seconds
        self.total_seconds = total_seconds
        self.running = False
        self.start_time = None
        
        # Frame for this record
        self.frame = tk.Frame(parent, bg="white", relief=tk.FLAT)
        self.frame.pack(pady=5, padx=10, fill=tk.X)
        
        # Labels
        self.channel_label = tk.Label(self.frame, text=f"Channel: {self.channel}", font=("Arial", 12), bg="white", width=16, anchor=tk.W)
        self.channel_label.grid(row=0, column=0, padx=10, sticky=tk.W)
        
        self.time_label = tk.Label(self.frame, text=self.format_time(self.total_seconds), font=("Arial", 16, "bold"), bg="white")
        self.time_label.grid(row=0, column=1, padx=10, sticky=tk.W)
        self.time_label.config(fg="red" if self.total_seconds < 0 else "black")
        
        # Delete button
        self.delete_button = tk.Button(self.frame, text="Delete", command=self.delete_record, bg="lightcoral", fg="white")
        self.delete_button.grid(row=0, column=2, padx=5, sticky=tk.E)

        self.frame.grid_columnconfigure(1, weight=1)
    
    def format_time(self, seconds):
        if seconds < 0:
            sign = "-"
            seconds = abs(seconds)
        else:
            sign = ""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{sign}{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def start_countdown(self):
        if not self.running:
            self.running = True
            self.start_time = time.monotonic()
    
    def delete_record(self):
        self.running = False
        self.frame.destroy()
        self.level_group.records.remove(self)

class LevelGroup:
    def __init__(self, parent, app, map_level):
        self.parent = parent
        self.app = app
        self.map_level = map_level
        self.records = []
        
        # Main frame for this level group
        self.group_frame = tk.Frame(parent, bg="lightgray", relief=tk.GROOVE, bd=2)
        self.group_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)
        
        # Level header
        self.header_frame = tk.Frame(self.group_frame, bg="darkgray")
        self.header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.level_label = tk.Label(self.header_frame, text=f"Map-Level: {self.map_level}", font=("Arial", 14, "bold"), bg="darkgray", fg="white")
        self.level_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Container for records
        self.records_frame = tk.Frame(self.group_frame, bg="white")
        self.records_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Input frame for adding records to this level
        self.input_frame = tk.Frame(self.group_frame, bg="lightgray")
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(self.input_frame, text="Channel:", bg="lightgray", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.channel_entry = tk.Entry(self.input_frame, width=10)
        self.channel_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(self.input_frame, text="Time (HHMM):", bg="lightgray", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.time_entry = tk.Entry(self.input_frame, width=15)
        self.time_entry.grid(row=0, column=3, padx=5)
        self.time_entry.bind('<Return>', lambda e: self.add_record())
        
        self.add_button = tk.Button(self.input_frame, text="Add Record", command=self.add_record, bg="lightblue")
        self.add_button.grid(row=0, column=4, padx=5)
    
    def parse_time(self, time_str):
        if len(time_str) == 4 and time_str.isdigit():
            h = int(time_str[0:2])
            m = int(time_str[2:4])
            if 0 <= m < 60:
                return h * 3600 + m * 60
        return None
    
    def add_record(self):
        channel_str = self.channel_entry.get()
        time_str = self.time_entry.get()
        
        if not channel_str or not time_str:
            messagebox.showerror("Input Error", "Please enter both Channel and Time (HHMM).")
            return
        
        try:
            channel = int(channel_str)
        except:
            messagebox.showerror("Input Error", "Channel must be a valid number.")
            return
        
        time_seconds = self.parse_time(time_str)
        if time_seconds is None:
            messagebox.showerror("Input Error", "Time must be 4 digits in HHMM format, with minutes 00-59.")
            return
        
        if any(record.channel == channel for record in self.records):
            messagebox.showerror("Input Error", f"Channel {channel} already exists in Level {self.map_level}.")
            return
        
        new_record = CountdownRecord(self.records_frame, self, channel, time_seconds)
        self.records.append(new_record)
        self._sort_records()
        new_record.start_countdown()
        
        # Clear entries
        self.channel_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

    def _sort_records(self):
        for record in sorted(self.records, key=lambda r: r.channel):
            record.frame.pack_forget()
            record.frame.pack(pady=5, padx=10, fill=tk.X)

class CountdownTimerApp:
    def __init__(self, root):
        self.root = root

        self.root.state('zoomed')  # Fullscreen mode
        self.root.title("Countdown Timer - Grouped by Level")
        
        # Main scrollable area
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Top input frame for creating new level groups
        self.top_input_frame = tk.Frame(root, bg="lightyellow", relief=tk.RAISED, bd=2)
        self.top_input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        tk.Label(self.top_input_frame, text="Create New Level Group:", bg="lightyellow", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(self.top_input_frame, text="Map-Level:", bg="lightyellow", font=("Arial", 10)).grid(row=0, column=1, padx=5)
        self.new_level_entry = tk.Entry(self.top_input_frame, width=10)
        self.new_level_entry.grid(row=0, column=2, padx=5)
        self.new_level_entry.bind('<Return>', lambda e: self.create_level_group())
        self.create_button = tk.Button(self.top_input_frame, text="Create Level", command=self.create_level_group, bg="lightgreen")
        self.create_button.grid(row=0, column=3, padx=5)
        
        # Dictionary to store level groups by level number
        self.level_groups = {}
        
        # Start global timer for all countdowns
        self.update_all_timers()
    
    def update_all_timers(self):
        now = time.monotonic()
        for level_group in self.level_groups.values():
            for record in level_group.records:
                if not record.running:
                    continue
                if record.start_time is None:
                    continue
                elapsed = int(now - record.start_time)
                remaining = record.start_seconds - elapsed
                if remaining <= -1800:
                    remaining = -1800
                    record.running = False
                if remaining != record.total_seconds:
                    record.total_seconds = remaining
                    record.time_label.config(text=record.format_time(record.total_seconds), fg="red" if record.total_seconds < 0 else "black")
        self.root.after(1000, self.update_all_timers)
    
    def create_level_group(self):
        level_str = self.new_level_entry.get()
        
        if not level_str:
            messagebox.showerror("Input Error", "Please enter a level number.")
            return
        
        try:
            level = int(level_str)
        except:
            messagebox.showerror("Input Error", "Map-Level must be a valid number.")
            return
        
        if level in self.level_groups:
            messagebox.showerror("Input Error", f"Level {level} already exists.")
            return
        
        # Create new level group
        new_group = LevelGroup(self.scrollable_frame, self, level)
        self.level_groups[level] = new_group
        
        # Sort by level number
        self._sort_level_groups()
        
        # Clear entry
        self.new_level_entry.delete(0, tk.END)
    
    def _sort_level_groups(self):
        # Reorder frames by level
        for level in sorted(self.level_groups.keys()):
            self.level_groups[level].group_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=False)

    def _on_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 * int(event.delta / 120)
        self.canvas.yview_scroll(delta, "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimerApp(root)
    root.mainloop()