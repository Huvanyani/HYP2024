import sqlite3
import hashlib
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self, db_name='password_manager.db'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """Sets up the database with required tables."""
        # Create users table
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT
                        )''')
        # Create passwords table
        self.c.execute('''CREATE TABLE IF NOT EXISTS passwords (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            site TEXT,
                            password TEXT,
                            key BLOB,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                        )''')
        self.conn.commit()

    def hash_password(self, password):
        """Hashes a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_key(self):
        """Generates a new encryption key."""
        return Fernet.generate_key()

    def encrypt_password(self, password, key):
        """Encrypts a password using the provided key."""
        f = Fernet(key)
        return f.encrypt(password.encode()).decode()

    def decrypt_password(self, password, key):
        """Decrypts a password using the provided key."""
        f = Fernet(key)
        return f.decrypt(password.encode()).decode()

    def register_user(self, username, password):
        """Registers a new user with a hashed password."""
        hashed_password = self.hash_password(password)
        try:
            self.c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username, password):
        """Logs in a user by checking the hashed password."""
        hashed_password = self.hash_password(password)
        self.c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        return self.c.fetchone()

    def add_password(self, user_id, site, password):
        """Adds a new password entry for the logged-in user."""
        key = self.generate_key()
        encrypted_password = self.encrypt_password(password, key)
        self.c.execute('INSERT INTO passwords (user_id, site, password, key) VALUES (?, ?, ?, ?)',
                       (user_id, site, encrypted_password, key))
        self.conn.commit()

    def update_password(self, user_id, site, password):
        """Updates an existing password entry for the logged-in user."""
        key = self.generate_key()
        encrypted_password = self.encrypt_password(password, key)
        self.c.execute('UPDATE passwords SET password = ?, key = ? WHERE user_id = ? AND site = ?',
                       (encrypted_password, key, user_id, site))
        self.conn.commit()

    def get_passwords(self, user_id):
        """Retrieves all password entries for the logged-in user."""
        self.c.execute('SELECT id, site, password, key FROM passwords WHERE user_id = ?', (user_id,))
        return self.c.fetchall()

    def get_password_details(self, password_id):
        """Retrieves password and key for a specific password entry."""
        self.c.execute('SELECT password, key FROM passwords WHERE id = ?', (password_id,))
        return self.c.fetchone()
