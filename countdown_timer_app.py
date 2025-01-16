import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyttsx3
import time
import re

class TimeParser:
    @staticmethod
    def parse_time_input(input_str):
        input_str = input_str.strip().lower()
        
        # Check for arithmetic expression first
        if any(op in input_str for op in ['+', '-', '*', '/']):
            return TimeParser.evaluate_arithmetic(input_str)
            
        # Handle time format (e.g., 5m30s, 5m, 30s)
        total_seconds = 0
        minutes_match = re.search(r'(\d+)m', input_str)
        seconds_match = re.search(r'(\d+)s', input_str)
        
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
        
        if total_seconds > 0:
            return total_seconds
            
        # If no valid format is found, try pure number (assumed seconds)
        if input_str.isdigit():
            return int(input_str)
            
        raise ValueError("Invalid time format. Use: '5m30s', '5m', '30s', or arithmetic (e.g., '2*60+30')")

    @staticmethod
    def evaluate_arithmetic(expr):
        expr = expr.replace('m', '*60').replace('s', '')
        if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expr):
            raise ValueError("Invalid arithmetic expression")
        try:
            result = eval(expr)
            if not isinstance(result, (int, float)) or result <= 0:
                raise ValueError("Expression must evaluate to a positive number")
            return int(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

class CountdownTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Countdown Timer")
        self.root.geometry("800x500")
        
        # Load the background image
        self.bg_image = Image.open("background.jpg")
        self.bg_image = self.bg_image.resize((800, 500), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a Frame and set the background image
        self.background_frame = ttk.Frame(root)
        self.background_frame.place(relwidth=1, relheight=1)

        # Create a label to hold the background image
        self.background_label = tk.Label(self.background_frame, image=self.bg_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Timer variables
        self.time_left = 0
        self.running = False
        self.paused = False

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Create UI elements
        self.label = ttk.Label(
            self.background_frame, 
            text="Enter time (e.g., 5m30s, 5m, 30s, or 2*60+30):", 
            font=("Helvetica", 14), 
            background="#ffffff"
        )
        self.label.pack(pady=20)

        self.entry = ttk.Entry(self.background_frame, font=("Helvetica", 12))
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', self.start_timer)

        self.start_button = ttk.Button(
            self.background_frame, 
            text="Start Timer", 
            command=self.start_timer
        )
        self.start_button.pack(pady=5)

        self.pause_button = ttk.Button(
            self.background_frame, 
            text="Pause Timer", 
            command=self.pause_timer
        )
        self.pause_button.pack(pady=5)

        self.resume_button = ttk.Button(
            self.background_frame, 
            text="Resume Timer", 
            command=self.resume_timer
        )
        self.resume_button.pack(pady=5)

        self.exit_button = ttk.Button(
            self.background_frame, 
            text="Exit", 
            command=self.exit_app
        )
        self.exit_button.pack(pady=5)

        self.time_display = ttk.Label(
            self.background_frame, 
            text="", 
            font=("Helvetica", 24), 
            background="#ffffff"
        )
        self.time_display.pack(pady=20)

    def start_timer(self, event=None):
        try:
            self.time_left = TimeParser.parse_time_input(self.entry.get())
            if self.time_left <= 0:
                raise ValueError("Time must be greater than zero.")
            self.running = True
            self.paused = False
            self.update_timer()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            self.time_display.config(text="00:00")

    def update_timer(self):
        if self.running and not self.paused:
            if self.time_left > 0:
                mins, secs = divmod(self.time_left, 60)
                self.time_display.config(text=f"{mins:02}:{secs:02}")
                self.announce_time(mins, secs)
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.time_display.config(text="Time's up!")
                self.engine.say("Time's up!")
                self.engine.runAndWait()
                self.running = False

    def announce_time(self, mins, secs):
        if self.time_left <= 5:
            self.engine.say(f"{self.time_left}")
            self.engine.runAndWait()

    def pause_timer(self):
        if self.running:
            self.paused = True

    def resume_timer(self):
        if self.running and self.paused:
            self.paused = False
            self.update_timer()

    def exit_app(self):
        self.root.destroy()

def countdown_timer_console(duration):
    try:
        seconds = TimeParser.parse_time_input(duration)
        print(f"Countdown started for {seconds} seconds.")
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            print(f"{mins:02}:{secs:02}", end="\r")
            time.sleep(1)
            seconds -= 1
        print("\nTime's up!")
    except ValueError as e:
        print(f"Error: {e}")

def main_menu():
    while True:
        print("\nChoose an option:")
        print("1. Console")
        print("2. GUI")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice in ['1', '2', '3']:
            if choice == '1':
                print("\nEnter countdown duration:")
                print("Examples: '5m30s', '5m', '30s', '2*60+30'")
                duration_input = input("Duration: ")
                countdown_timer_console(duration_input)
            elif choice == '2':
                root = tk.Tk()
                app = CountdownTimerApp(root)
                root.protocol("WM_DELETE_WINDOW", app.exit_app)
                root.mainloop()
            elif choice == '3':
                print("Exiting the application.")
                break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()

