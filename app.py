# Import simple Tk dialog helpers for login
import tkinter as tk
from tkinter import messagebox, simpledialog

# Import app services and window
from src.gui.main_window import MainWindow
from src.services.auth_service import AuthService


def prompt_login(auth_service):
    # Create a hidden root so we can show simple dialogs before the main window.
    login_root = tk.Tk()
    login_root.withdraw()

    username = simpledialog.askstring("Login", "Username:", parent=login_root)
    if not username:
        messagebox.showerror("Login Failed", "Username is required.", parent=login_root)
        login_root.destroy()
        return None

    password = simpledialog.askstring("Login", "Password:", show="*", parent=login_root)
    if not password:
        messagebox.showerror("Login Failed", "Password is required.", parent=login_root)
        login_root.destroy()
        return None

    user = auth_service.authenticate(username.strip(), password)
    if user is None:
        messagebox.showerror("Login Failed", "Invalid username or password.", parent=login_root)
        login_root.destroy()
        return None

    login_root.destroy()
    return user

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