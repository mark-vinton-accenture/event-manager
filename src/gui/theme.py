import tkinter as tk
from tkinter import ttk

BG       = "#0D1B2A"
PANEL    = "#152338"
ENTRY_BG = "#0A1628"
PRIMARY  = "#1565C0"
SUCCESS  = "#2E7D32"
TEXT     = "#E8F0FE"
LABEL    = "#90CAF9"
ACCENT   = "#42A5F5"
BORDER   = "#1E4080"
FONT     = "Segoe UI"


def apply(root):
    s = ttk.Style(root)
    s.theme_use('clam')
    s.configure('.', background=BG, foreground=TEXT, font=(FONT, 10))
    s.configure('TLabel', background=BG, foreground=LABEL)
    s.configure('TFrame', background=BG)
    s.configure('TEntry',
        fieldbackground=ENTRY_BG, foreground=TEXT,
        insertcolor=TEXT, bordercolor=BORDER,
        lightcolor=BORDER, darkcolor=BORDER, selectbackground=PRIMARY)
    s.configure('TButton',
        background=PRIMARY, foreground='white', bordercolor=PRIMARY,
        lightcolor='#1976D2', darkcolor='#0D47A1', padding=(12, 5))
    s.map('TButton',
        background=[('active', '#1976D2'), ('pressed', '#0D47A1')],
        foreground=[('active', 'white')])
    s.configure('Accent.TButton',
        background=SUCCESS, foreground='white', bordercolor=SUCCESS,
        lightcolor='#388E3C', darkcolor='#1B5E20', padding=(12, 5))
    s.map('Accent.TButton',
        background=[('active', '#388E3C'), ('pressed', '#1B5E20')],
        foreground=[('active', 'white')])
