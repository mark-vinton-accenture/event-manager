#Create a main window for the application using Tkinter, has a title of Event Manager and a size of 400x300 pixels. The window should contain a label that says "Welcome to the Main Window!" and a button that says "Click Me". When the button is clicked, the label should change to say "Button Clicked!"
import tkinter as tk
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Event Manager")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Welcome to the Main Window!")
        self.label.pack(pady=20)

        self.button = tk.Button(self, text="Click Me", command=self.on_button_click)
        self.button.pack(pady=10)

    def on_button_click(self):
        self.label.config(text="Button Clicked!")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

