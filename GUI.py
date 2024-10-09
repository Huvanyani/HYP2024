import re
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
        # Initializing the main window
        self.root.title("Password Manager")
        self.show_welcome_screen()

    def show_welcome_screen(self):
        # Displaying the welcome screen with Register and Login options.
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Welcome", font=('Arial', 16)).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Register", command=self.show_register_screen).grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        tk.Button(self.root, text="Login", command=self.show_login_screen).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def show_register_screen(self):
        # Displays the register screen along with its components.
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Registration", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.root, text="Name:").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Username:").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Password:").grid(row=3, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Contact:").grid(row=4, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Confirm Contact:").grid(row=5, column=0, padx=10, pady=10)

        # defining register textboxes
        self.name_entry = tk.Entry(self.root)
        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")
        self.contact_entry = tk.Entry(self.root)
        self.confirm_contact_entry = tk.Entry(self.root)

        # placing the textboxes on the UI
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)
        self.username_entry.grid(row=2, column=1, padx=10, pady=10)
        self.password_entry.grid(row=3, column=1, padx=10, pady=10)
        self.contact_entry.grid(row=4, column=1, padx=10, pady=10)
        self.confirm_contact_entry.grid(row=5, column=1, padx=10, pady=10)

        # Enrollment will now trigger registration automatically after face capture
        tk.Button(self.root, text="Enroll & Register", command=self.enroll_face_and_register).grid(row=6, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Back", command=self.show_welcome_screen).grid(row=6, column=1, padx=10, pady=10)

    def enroll_face_and_register(self):
        # Validates the fields and enrolls face; registers user automatically after face enrollment.

        # Get user details
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        contact = self.contact_entry.get().strip()
        confirm_contact = self.confirm_contact_entry.get().strip()

        # Validate contact number using regex
        contact_regex = r"^0\d{9}$"  # 10 digits, starting with 0
        if not re.match(contact_regex, contact):
            messagebox.showerror('Error', 'Invalid contact number. It should be 10 digits starting with 0.')
            return

        # Validate password using regex
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_regex, password):
            messagebox.showerror('Error', 'Password must have at least 8 characters, 1 digit, 1 special character, and 1 alphabet.')
            return

        # Ensure contact numbers match
        if contact != confirm_contact:
            messagebox.showerror('Error', 'Contact fields do not match.')
            return

        # Proceed with face capture and registration if validation passes
        success = self.enroll.capture_face(username)

        if success:
            # After capturing the face, proceed with registration
            self.register_user(name, username, password, contact)
        else:
            # If face capture failed, show error message
            messagebox.showerror('Error', 'Face enrollment failed. Please try again.')

    def register_user(self, name, username, password, contact):
        # Registers a new user and adds them to the database.
        if self.password_manager.register_user(username, password, name, contact):
            messagebox.showinfo('Success', 'Registration successful!')
            self.show_login_screen()
        else:
            messagebox.showerror('Error', 'Username already exists.')

    def show_login_screen(self):
        # Displaying the login screen with components.
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Login", font=('Arial', 14)).grid(row=0, column=0, columnspan=3, pady=10)
        tk.Label(self.root, text="Username:").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Password:").grid(row=2, column=0, padx=10, pady=10)

        self.login_username_entry = tk.Entry(self.root)
        self.login_password_entry = tk.Entry(self.root, show="*")

        self.login_username_entry.grid(row=1, column=1, padx=10, pady=10)
        self.login_password_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Login", command=self.login).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Verify Face", command=self.verify_face).grid(row=3, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Back", command=self.show_welcome_screen).grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    def login(self):
        # Logs in a user based on username and password
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()
        user = self.password_manager.login_user(username, password)
        if user:
            self.current_user_id = user[0]
            messagebox.showinfo('Success', 'Login successful!')
            self.show_dashboard()
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def verify_face(self):
        # Verifies the user's face before allowing access
        username = self.login_username_entry.get().strip()
        threshold = 0.4  # Set the threshold for face verification
        if self.verification.verify_face(username, threshold):
            user = self.password_manager.login_user(username, None)  # Assuming login_user can handle None password for face verification
            if user:
                self.current_user_id = user[0]
                messagebox.showinfo('Success', 'Face verification successful!')
                self.show_dashboard()
            else:
                messagebox.showerror('Error', 'Face verification failed. No matching user found.')
        else:
            messagebox.showerror('Error', 'Face verification failed.')

    def show_dashboard(self):
        # Displays the main dashboard for the logged-in user.
        for widget in self.root.winfo_children():
            widget.destroy()

        # defining and placing labels on the dashboard UI
        tk.Label(self.root, text="Site:", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
        tk.Label(self.root, text="Password:", font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=10, sticky='e')

        # defining textboxes for the dashboard
        self.site_entry = tk.Entry(self.root, width=30)
        self.password_entry = tk.Entry(self.root, width=30)

        # placing the textboxes on the UI
        self.site_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        # defining and placing buttons for dashboard actions
        tk.Button(self.root, text="Generate Password", command=self.generate_password).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Add Password", command=self.add_password).grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Update Password", command=self.update_password).grid(row=2, column=2, padx=10, pady=10)
        tk.Button(self.root, text="Logout", command=self.logout).grid(row=2, column=3, padx=10, pady=10)

        # creating a treeview to display the passwords and site names on
        self.password_list = ttk.Treeview(self.root, columns=('ID', 'Site', 'Password', 'Copy'), show='headings')
        self.password_list.heading('ID', text='ID')
        self.password_list.heading('Site', text='Site')
        self.password_list.heading('Password', text='Password')
        self.password_list.heading('Copy', text='Action')
        self.password_list.column('ID', width=0, stretch=tk.NO)  # Hiding the ID column for better view
        self.password_list.column('Copy', width=100)
        self.password_list.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        self.password_list.bind('<Double-1>', self.on_copy_button_click)
        self.show_passwords()

    def logout(self):
        # Logs out the user and returns to the welcome screen.
        self.current_user_id = None
        self.show_welcome_screen()

    def generate_password(self):
        # Generates a secure password using the secrets class and displays it.
        length = 16
        password = secrets.token_urlsafe(length)[:length]
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def add_password(self):
        # Adds a new password to the list.
        site = self.site_entry.get().strip()
        password = self.password_entry.get().strip()
        if not site or not password:
            messagebox.showerror('Error', 'Site and Password fields cannot be empty.')
            return
        self.password_manager.add_password(self.current_user_id, site, password)
        messagebox.showinfo('Success', 'Password added!')
        self.show_passwords()

    def update_password(self):
        # Updates an existing password entry.
        site = self.site_entry.get().strip()
        password = self.password_entry.get().strip()
        if not site or not password:
            messagebox.showerror('Error', 'Site and Password fields cannot be empty.')
            return
        self.password_manager.update_password(self.current_user_id, site, password)
        messagebox.showinfo('Success', 'Password updated!')
        self.show_passwords()

    def show_passwords(self):
        # Displays all password entries for the logged-in user.

        # clearing the tree before showing new information
        for item in self.password_list.get_children():
            self.password_list.delete(item)

        # getting the passwords for the current user
        passwords = self.password_manager.get_passwords(self.current_user_id)
        for i, (password_id, site, encrypted_password, key) in enumerate(passwords):
            self.password_list.insert('', 'end', values=(password_id, site, '******', 'Copy'))

    def on_copy_button_click(self, event):
        # Handles the click event on the copy button in the treeview.
        selected_item = self.password_list.selection()[0]
        password_id = self.password_list.item(selected_item, 'values')[0]
        self.copy_password(password_id)

    def copy_password(self, password_id):
        # Decrypts the password and shows it in a popup after verifying the user's face.

        # Get the username based on the current user's ID
        username = self.password_manager.get_username_by_id(self.current_user_id)

        if username:
            # Perform face verification with a threshold of 0.6
            threshold = 0.6
            face_verified = self.verification.verify_face(username, threshold)

            if face_verified:
                # If the face is verified, proceed to decrypt and show the password
                encrypted_password, key = self.password_manager.get_password_details(password_id)
                if key is None:
                    decrypted_password = "Error: Missing key"
                else:
                    try:
                        decrypted_password = self.password_manager.decrypt_password(encrypted_password, key)
                    except Exception as e:
                        decrypted_password = f"Error: {str(e)}"

                # Show the decrypted password in a popup window
                popup = tk.Toplevel()
                popup.title("Copy Password")
                tk.Label(popup, text="Password:").grid(row=0, column=0, padx=10, pady=10)
                password_entry = tk.Entry(popup, width=30)
                password_entry.grid(row=0, column=1, padx=10, pady=10)
                password_entry.insert(0, decrypted_password)
                password_entry.focus_set()

                # Optionally, you can add a button to copy the password to the clipboard
                tk.Button(popup, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(decrypted_password)).grid(row=1, column=0, padx=10, pady=10)
                tk.Button(popup, text="Close", command=popup.destroy).grid(row=1, column=1, padx=10, pady=10)
            else:
                # displaying an error message for when face verification fails
                messagebox.showerror('Error', 'Face verification failed. You are not authorized to copy this password.')
        else:
            messagebox.showerror('Error', 'User not found. Unable to retrieve username.')

    def copy_to_clipboard(self, text):
        # Copies the given text to the clipboard.
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # now it stays on the clipboard after the window is closed
        messagebox.showinfo('Copied', 'Password copied to clipboard!')
