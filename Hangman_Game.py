import customtkinter as ctk
import random
import json
import time
from CTkMessagebox import CTkMessagebox
from datetime import datetime

class HangmanGame:
    def __init__(self, root):
        self.words = [
            "PYTHON", "JAVASCRIPT", "JAVA", "RUBY", "SWIFT",
            "KOTLIN", "HTML", "CSS", "REACT", "ANGULAR",
            "VUE", "NODE", "DJANGO", "FLASK", "TENSORFLOW"
        ]
        self.difficulties = {"Easy": 8, "Normal": 6, "Hard": 5}
        self.root = root
        self.root.title("Hangman Game")
        self.root.geometry("600x650")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Initialize UI and game
        self.create_menu()

    def create_menu(self):
        # Difficulty selection and start button
        self.menu_frame = ctk.CTkFrame(self.root)
        self.menu_frame.grid(row=0, column=0, pady=20)

        ctk.CTkLabel(self.menu_frame, text="Select Difficulty:", font=("Arial", 18)).pack(pady=5)
        self.diff_var = ctk.StringVar(value="Normal")
        for level in self.difficulties:
            ctk.CTkRadioButton(
                self.menu_frame, text=level, variable=self.diff_var, value=level
            ).pack(anchor="w", padx=20)

        self.start_button = ctk.CTkButton(
            self.menu_frame, text="Start Game", command=self.start_game
        )
        self.start_button.pack(pady=10)

    def start_game(self):
        # Remove menu and set difficulty
        self.menu_frame.destroy()
        self.max_attempts = self.difficulties[self.diff_var.get()]

        self.setup_game_variables()
        self.create_widgets()
        self.update_word_display()
        self.start_timer()  # start global timer

    def setup_game_variables(self):
        self.selected_word = random.choice(self.words)
        self.guessed_letters = []
        self.remaining_attempts = self.max_attempts
        self.game_over = False
        self.stage_index = 0
        self.start_time = None
        self.guess_time_limit = 10  # seconds per guess
        self.current_timer = None

    def create_widgets(self):
        # Canvas for hangman drawing
        self.hangman_canvas = ctk.CTkCanvas(self.root, width=200, height=200, bg="white")
        self.hangman_canvas.grid(row=0, column=0, pady=10)

        # Word display
        self.word_label = ctk.CTkLabel(self.root, text="_ " * len(self.selected_word), font=("Arial", 24))
        self.word_label.grid(row=1, column=0, pady=5)

        # Guessed letters display
        self.guessed_label = ctk.CTkLabel(self.root, text="Guessed: []", font=("Arial", 14))
        self.guessed_label.grid(row=2, column=0, pady=5)

        # Guess input with validation to single char
        vcmd = (self.root.register(self.validate_char), '%P')
        self.guess_entry = ctk.CTkEntry(
            self.root, width=50, font=("Arial", 16), validate="key", validatecommand=vcmd
        )
        self.guess_entry.grid(row=3, column=0, pady=5)

        # Guess button
        self.guess_button = ctk.CTkButton(self.root, text="Guess", command=self.process_guess)
        self.guess_button.grid(row=4, column=0, pady=5)

        # Status labels
        self.attempts_label = ctk.CTkLabel(self.root, text=f"Attempts left: {self.remaining_attempts}")
        self.attempts_label.grid(row=5, column=0)

        self.timer_label = ctk.CTkLabel(self.root, text=f"Time left: {self.guess_time_limit}")
        self.timer_label.grid(row=6, column=0)

        self.status_label = ctk.CTkLabel(self.root, text="")
        self.status_label.grid(row=7, column=0, pady=5)

        # Reset button
        self.reset_button = ctk.CTkButton(
            self.root, text="RESET", command=self.reset_game,
            fg_color="#D32F2F", hover_color="#B71C1C"
        )
        self.reset_button.grid(row=8, column=0, pady=10)

    def validate_char(self, new_text):
        return new_text.isalpha() and len(new_text) <= 1 or new_text == ""

    def draw_next_stage(self):
        stages = [
            lambda: self.hangman_canvas.create_line(50, 180, 150, 180),
            lambda: self.hangman_canvas.create_line(100, 180, 100, 50),
            lambda: self.hangman_canvas.create_line(100, 50, 150, 50),
            lambda: self.hangman_canvas.create_line(150, 50, 150, 70),
            lambda: self.hangman_canvas.create_oval(140, 70, 160, 90),
            lambda: self.hangman_canvas.create_line(150, 90, 150, 130),
            lambda: self.hangman_canvas.create_line(150, 100, 130, 80),
            lambda: self.hangman_canvas.create_line(150, 100, 170, 80),
            lambda: self.hangman_canvas.create_line(150, 130, 130, 160),
            lambda: self.hangman_canvas.create_line(150, 130, 170, 160)
        ]
        if self.stage_index < len(stages):
            stages[self.stage_index]()
            self.stage_index += 1

    def update_word_display(self):
        display = [letter if letter in self.guessed_letters else '_' for letter in self.selected_word]
        self.word_label.configure(text=' '.join(display))
        self.guessed_label.configure(text=f"Guessed: {self.guessed_letters}")

    def process_guess(self):
        if self.game_over:
            return
        # Stop current timer
        if self.current_timer:
            self.root.after_cancel(self.current_timer)

        guess = self.guess_entry.get().upper()
        self.guess_entry.delete(0, 'end')

        if not guess:
            self.status_label.configure(text="Please enter a letter!", text_color="red")
            self.start_guess_timer()
            return

        if guess in self.guessed_letters:
            self.status_label.configure(text="You already guessed that letter!", text_color="orange")
            self.start_guess_timer()
            return

        self.guessed_letters.append(guess)

        if guess not in self.selected_word:
            self.remaining_attempts -= 1
            self.attempts_label.configure(text=f"Attempts left: {self.remaining_attempts}")
            self.draw_next_stage()

        self.update_word_display()
        self.check_game_status()
        if not self.game_over:
            self.start_guess_timer()

    def check_game_status(self):
        if all(letter in self.guessed_letters for letter in self.selected_word):
            self.end_game(win=True)
        elif self.remaining_attempts <= 0:
            self.end_game(win=False)

    def end_game(self, win: bool):
        self.game_over = True
        if self.current_timer:
            self.root.after_cancel(self.current_timer)
        self.guess_entry.configure(state='disabled')
        self.guess_button.configure(state='disabled')

        elapsed = int(time.time() - self.start_time)
        record = {
            "word": self.selected_word,
            "win": win,
            "attempts_left": self.remaining_attempts,
            "difficulty": self.diff_var.get(),
            "time_taken": elapsed,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_record(record)

        if win:
            msg = "Congratulations! You won!"
            self.status_label.configure(text=msg, text_color="green")
            CTkMessagebox(icon="check", message=msg, title="You win!")
        else:
            msg = f"Game Over! The word was: {self.selected_word}"
            self.status_label.configure(text=msg, text_color="red")
            CTkMessagebox(title="You lose!", message=msg, icon="info")

    def reset_game(self):
        if self.current_timer:
            self.root.after_cancel(self.current_timer)
        self.hangman_canvas.delete("all")
        self.setup_game_variables()
        self.attempts_label.configure(text=f"Attempts left: {self.remaining_attempts}")
        self.status_label.configure(text="")
        self.word_label.configure(text="_ " * len(self.selected_word))
        self.guessed_label.configure(text="Guessed: []")
        self.guess_entry.configure(state='normal')
        self.guess_button.configure(state='normal')
        self.start_timer()  # reset global and per-guess timer


    def start_timer(self):
        # Global start time
        self.start_time = time.time()
        self.start_guess_timer()

    def start_guess_timer(self):
        self.time_left = self.guess_time_limit
        self.update_timer()

    def update_timer(self):
        self.timer_label.configure(text=f"Time left: {self.time_left}")
        if self.time_left <= 0:
            self.status_label.configure(text="Time's up!", text_color="red")
            self.process_timeout()
        else:
            self.time_left -= 1
            self.current_timer = self.root.after(1000, self.update_timer)

    def process_timeout(self):
        self.remaining_attempts -= 1
        self.attempts_label.configure(text=f"Attempts left: {self.remaining_attempts}")
        self.draw_next_stage()
        self.update_word_display()
        self.check_game_status()
        if not self.game_over:
            self.start_guess_timer()

    def save_record(self, record):
        try:
            with open('records.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        data.append(record)
        with open('records.json', 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == '__main__':
    root = ctk.CTk()
    game = HangmanGame(root)
    root.mainloop()
