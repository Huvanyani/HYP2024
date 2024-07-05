import tkinter as tk
from PasswordManager import PasswordManager
from GUI import GUI

class Main:
    def __init__(self):
        """Initializes the main application."""
        self.root = tk.Tk()
        self.password_manager = PasswordManager()
        self.gui = GUI(self.root, self.password_manager)

    def run(self):
        """Runs the main application loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = Main()
    app.run()
