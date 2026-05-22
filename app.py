import os
import tkinter as tk
from tkinter import messagebox, ttk

from src.gui.main_window import MainWindow
from src.services.auth_service import AuthService
from src.gui import theme


class LoginDialog(tk.Toplevel):
    def __init__(self, parent, auth_service):
        super().__init__(parent)
        self.auth_service = auth_service
        self.user = None
        self.title("AtTheFunc Event Manager - Login")
        self.configure(bg=theme.BG)
        self.resizable(False, False)

        # Header
        header = tk.Frame(self, bg=theme.PANEL)
        header.pack(fill='x')

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.png")
        if os.path.exists(logo_path):
            self.logo_image = tk.PhotoImage(file=logo_path)
            if self.logo_image.width() > 160:
                scale = max(1, self.logo_image.width() // 160)
                self.logo_image = self.logo_image.subsample(scale, scale)
            tk.Label(header, image=self.logo_image, bg=theme.PANEL).pack(pady=(12, 4))

        tk.Label(
            header,
            text="Welcome to AtTheFunc",
            font=(theme.FONT, 14, 'bold'),
            bg=theme.PANEL,
            fg=theme.ACCENT,
        ).pack(pady=(0, 12))

        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill='x')

        # Form
        form = tk.Frame(self, bg=theme.BG)
        form.pack(padx=30, pady=15)

        ttk.Label(form, text="Username").pack(anchor='w', pady=(8, 2))
        self.username_entry = ttk.Entry(form, width=30)
        self.username_entry.pack()

        ttk.Label(form, text="Password").pack(anchor='w', pady=(8, 2))
        self.password_entry = ttk.Entry(form, width=30, show="*")
        self.password_entry.pack()

        # Buttons
        btn_frame = tk.Frame(self, bg=theme.BG)
        btn_frame.pack(pady=(4, 20))
        ttk.Button(btn_frame, text="Login", command=self.login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Create Account", command=self.create_account,
                   style='Accent.TButton').pack(side="left", padx=5)

        self.update_idletasks()
        width = max(self.winfo_width(), 320)
        height = self.winfo_height() + 20
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

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
    theme.apply(root)
    dialog = LoginDialog(root, auth_service)
    root.destroy()
    return dialog.user


if __name__ == "__main__":
    auth_service = AuthService()
    current_user = prompt_login(auth_service)

    if current_user is None:
        raise SystemExit(1)

    app = MainWindow(current_user=current_user)
    app.mainloop()
