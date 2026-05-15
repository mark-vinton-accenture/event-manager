# Import simple Tk dialog helpers for login
import tkinter as tk
from tkinter import messagebox, ttk

# Import app services and window
from src.gui.main_window import MainWindow
from src.services.auth_service import AuthService


class LoginDialog(tk.Toplevel):
    def __init__(self, parent, auth_service):
        super().__init__(parent)
        self.auth_service = auth_service
        self.user = None
        self.title("AtTheFunc Event Manager - Login")
        self.geometry("300x200")
        self.configure(bg='black')
        self.resizable(False, False)

        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f'+{x}+{y}')

        # Title
        title_label = ttk.Label(self, text="Welcome to AtTheFunc", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Username
        ttk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack()

        # Password
        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack()

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Login", command=self.login).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Create Account", command=self.create_account).pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self.wait_window()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return
        user = self.auth_service.authenticate(username, password)
        if user:
            self.user = user
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return
        if self.auth_service.register(username, password):
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Username already exists.")

    def on_close(self):
        self.user = None
        self.destroy()


def prompt_login(auth_service):
    root = tk.Tk()
    root.withdraw()
    dialog = LoginDialog(root, auth_service)
    root.destroy()
    return dialog.user

# This is the entry point of the program.
# Python sets __name__ to "__main__" only when you run this file directly
# (e.g. "python app.py"). If another file imports this one, this block is skipped.
if __name__ == "__main__":
    auth_service = AuthService()
    current_user = prompt_login(auth_service)

    if current_user is None:
        raise SystemExit(1)

    # Create the main application window
    app = MainWindow(current_user=current_user)

    # Start the tkinter event loop — this keeps the window open and
    # listens for things like button clicks until the user closes it
    app.mainloop()