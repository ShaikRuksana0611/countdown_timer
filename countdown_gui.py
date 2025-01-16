import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pyttsx3
import re

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Countdown Timer")
        
        # Initialize variables
        self.countdown_active = False
        self.is_paused = False
        self.time_left = 0
        self.countdown_job = None
        self.engine = pyttsx3.init()
        
        # Set up the window
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.resizable(False, False)
        
        # Set up UI
        self.setup_background()
        self.create_widgets()
        
    def setup_background(self):
        bg_image = Image.open("background.jpg")
        bg_image = bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.background_label = tk.Label(self.root, image=self.bg_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_widgets(self):
        # Entry label
        self.entry_label = tk.Label(
            self.root, 
            text="Enter time (e.g., 30s, 5m, or 2*30+15):", 
            font=("Arial", 20), 
            bg="white"
        )
        self.entry_label.pack(pady=20)

        # Entry widget
        self.entry = tk.Entry(self.root, font=("Arial", 20))
        self.entry.pack(pady=10)
        self.entry.focus()
        self.root.bind("<Return>", self.start_countdown)

        # Button frame
        self.button_frame = tk.Frame(self.root, bg="white")
        self.button_frame.pack(pady=20)

        # Start button
        self.start_button = tk.Button(
            self.button_frame,
            text="Start Countdown",
            command=self.start_countdown,
            font=("Arial", 20),
            bg="green",
            fg="white",
            width=15,
            height=2
        )
        self.start_button.pack(side="left", padx=20)

        # Pause button
        self.pause_button = tk.Button(
            self.button_frame,
            text="Pause",
            command=self.pause_resume_countdown,
            font=("Arial", 20),
            bg="orange",
            fg="white",
            width=15,
            height=2,
            state="disabled"
        )
        self.pause_button.pack(side="left", padx=20)

        # Exit button
        self.exit_button = tk.Button(
            self.root,
            text="Exit",
            command=self.exit_app,
            font=("Arial", 20),
            bg="blue",
            fg="white",
            width=15,
            height=2
        )
        self.exit_button.pack(pady=30)

        # Time display label
        self.time_label = tk.Label(
            self.root,
            text="Time Left: 0",
            font=("Arial", 30),
            bg="white"
        )
        self.time_label.pack(pady=20)

    def safe_eval(self, expr):
        expr = expr.replace(" ", "")
        # Handle time units
        if expr.endswith('s'):
            expr = expr[:-1]
        elif expr.endswith('m'):
            expr = f"{expr[:-1]}*60"
            
        if not re.match(r'^[\d\+\-\*/\(\)]+$', expr):
            raise ValueError("Invalid expression: Only numbers and arithmetic operators allowed")
        try:
            result = eval(expr)
            if not isinstance(result, (int, float)):
                raise ValueError("Expression must evaluate to a number")
            return int(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

    def start_countdown(self, event=None):
        if not self.countdown_active:
            try:
                input_time = self.entry.get().strip()
                self.time_left = self.safe_eval(input_time)
                if self.time_left <= 0:
                    raise ValueError("Time must be greater than zero")
                
                self.countdown_active = True
                self.is_paused = False
                self.start_button.config(state="disabled")
                self.pause_button.config(state="normal")
                self.countdown()
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))

    def pause_resume_countdown(self):
        if self.countdown_active:
            if self.is_paused:
                # Resume
                self.is_paused = False
                self.pause_button.config(text="Pause", bg="orange")
                self.countdown()
            else:
                # Pause
                self.is_paused = True
                self.pause_button.config(text="Resume", bg="yellow")
                if self.countdown_job:
                    self.root.after_cancel(self.countdown_job)

    def countdown(self):
        if self.countdown_active and not self.is_paused and self.time_left > 0:
            minutes, seconds = divmod(self.time_left, 60)
            self.time_label.config(text=f"Time Left: {minutes}m {seconds}s")
            
            if self.time_left <= 5:
                self.engine.say(str(self.time_left))
                self.engine.runAndWait()
            
            self.time_left -= 1
            self.countdown_job = self.root.after(1000, self.countdown)
        elif self.time_left <= 0 and not self.is_paused:
            self.time_label.config(text="Time's up!")
            self.engine.say("Time's up!")
            self.engine.runAndWait()
            self.reset_timer()

    def reset_timer(self):
        self.countdown_active = False
        self.is_paused = False
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pause", bg="orange")
        self.time_left = 0

    def exit_app(self):
        self.engine.stop()
        self.root.quit()

def main():
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
