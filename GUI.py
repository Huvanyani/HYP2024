import tkinter as tk
from tkinter import messagebox, ttk
import secrets
from enroll import Enroll
from verification import Verification


class GUI:
    def __init__(self, root, password_manager):
        self.root = root
        self.password_manager = password_manager
        self.current_user_id = None
        self.enroll = Enroll()
        self.verification = Verification()
        self.setup_ui()

    def setup_ui(self):
        """Initializes the main window and displays the login screen."""
        self.root.title("Password Manager")
        self.__sizeof__()
        self.show_login_screen()

    def show_login_screen(self):
        """Displays the login screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Username:").grid(row=0, column=0)
        tk.Label(self.root, text="Password:").grid(row=1, column=0)

        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Register", command=self.register).grid(row=2, column=0)
        tk.Button(self.root, text="Login", command=self.login).grid(row=2, column=1)
        tk.Button(self.root, text="Face", command=self.verification.verify_face).grid(row=2, column=2)

    def register(self):
        """Registers a new user."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.password_manager.register_user(username, password):
            messagebox.showinfo('Success', 'Registration successful!')
        else:
            messagebox.showerror('Error', 'Username already exists')

    def login(self):
        """Logs in a user."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.password_manager.login_user(username, password)
        if user:
            self.current_user_id = user[0]
            messagebox.showinfo('Success', 'Login successful!')
            self.show_dashboard()
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def show_dashboard(self):
        """Displays the main dashboard for the logged-in user."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Site:").grid(row=0, column=0)
        tk.Label(self.root, text="Password:").grid(row=1, column=0)

        self.site_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root)

        self.site_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Generate Password", command=self.generate_password).grid(row=2, column=0)
        tk.Button(self.root, text="Add Password", command=self.add_password).grid(row=2, column=1)
        tk.Button(self.root, text="Update Password", command=self.update_password).grid(row=2, column=2)
        # tk.Button(self.root, text="Face", command=self.enroll.capture_face).grid(row=2, column=3)

        self.password_list = ttk.Treeview(self.root, columns=('ID', 'Site', 'Password', 'Copy'), show='headings')
        self.password_list.heading('ID', text='ID')
        self.password_list.heading('Site', text='Site')
        self.password_list.heading('Password', text='Password')
        self.password_list.heading('Copy', text='Action')
        # self.password_list.column('ID', width=0, stretch=tk.NO)  # Hide the ID column
        self.password_list.column('Copy', width=100)
        self.password_list.grid(row=3, column=0, columnspan=4)

        self.password_list.bind('<Double-1>', self.on_copy_button_click)
        self.show_passwords()

    def generate_password(self):
        """Generates a secure password and displays it."""
        length = 16
        password = secrets.token_urlsafe(length)[:length]
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def add_password(self):
        """Adds a new password entry."""
        site = self.site_entry.get()
        password = self.password_entry.get()
        self.password_manager.add_password(self.current_user_id, site, password)
        messagebox.showinfo('Success', 'Password added!')
        self.show_passwords()

    def update_password(self):
        """Updates an existing password entry."""
        site = self.site_entry.get()
        password = self.password_entry.get()
        self.password_manager.update_password(self.current_user_id, site, password)
        messagebox.showinfo('Success', 'Password updated!')
        self.show_passwords()

    def show_passwords(self):
        """Displays all password entries for the logged-in user."""
        for item in self.password_list.get_children():
            self.password_list.delete(item)

        passwords = self.password_manager.get_passwords(self.current_user_id)
        for i, (password_id, site, encrypted_password, key) in enumerate(passwords):
            self.password_list.insert('', 'end', values=(password_id, site, '******', 'Copy'))

    def on_copy_button_click(self, event):
        """Handles the click event on the copy button in the Treeview."""
        selected_item = self.password_list.selection()[0]
        password_id = self.password_list.item(selected_item, 'values')[0]
        self.copy_password(password_id)

    def copy_password(self, password_id):
        """Decrypts the password and shows it in a popup for copying."""
        encrypted_password, key = self.password_manager.get_password_details(password_id)
        if key is None:
            decrypted_password = "Error: Missing key"
        else:
            try:
                decrypted_password = self.password_manager.decrypt_password(encrypted_password, key)
            except Exception as e:
                decrypted_password = f"Error: {str(e)}"

        popup = tk.Toplevel()
        popup.title("Copy Password")
        tk.Label(popup, text="Password:").grid(row=0, column=0)
        password_entry = tk.Entry(popup)
        password_entry.grid(row=0, column=1)
        password_entry.insert(0, decrypted_password)
        tk.Button(popup, text="Close", command=popup.destroy).grid(row=1, column=0, columnspan=2)
