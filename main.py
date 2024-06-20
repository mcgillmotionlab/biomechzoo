# main.py

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import events, processing, settings

class EnsemblerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ensembler GUI")

        print("Creating left frame")
        self.left_frame = ttk.Frame(self.root, width=200, relief=tk.SUNKEN)
        self.left_frame.pack(side="left", fill="y", padx=5, pady=5)

        print("Creating upload button")
        self.upload_button = ttk.Button(self.left_frame, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=10)

        print("Creating file label")
        self.file_label = ttk.Label(self.left_frame, text="No file uploaded")
        self.file_label.pack(pady=10)

        print("Creating middle frame")
        self.middle_frame = ttk.Frame(self.root, width=400, relief=tk.SUNKEN)
        self.middle_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.middle_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        print("Creating right frame")
        self.right_frame = ttk.Frame(self.root, width=200, relief=tk.SUNKEN)
        self.right_frame.pack(side="right", fill="y", padx=5, pady=5)

        print("Creating settings label")
        self.settings_label = ttk.Label(self.right_frame, text="Settings")
        self.settings_label.pack(pady=10)

        print("Creating option menu")
        self.setting_option = tk.StringVar(value="Option 1")
        self.option_menu = ttk.OptionMenu(self.right_frame, self.setting_option, "Option 1", *settings.get_settings().keys(), command=self.apply_setting)
        self.option_menu.pack(pady=10)

        # Add Exit Button
        print("Creating exit button")
        self.exit_button = ttk.Button(self.right_frame, text="Exit", command=self.close_window)
        self.exit_button.pack(pady=10)

    def upload_file(self):
        print("Upload button clicked")
        file_path = filedialog.askopenfilename()
        if file_path:
            print(f"File uploaded: {file_path}")
            self.file_label.config(text=file_path)
            data = processing.process_file(file_path)
            self.plot_data(data)
            events.on_file_upload(file_path)

    def plot_data(self, data):
        print("Plotting data")
        self.ax.clear()
        self.ax.plot(data)
        self.canvas.draw()

    def apply_setting(self, selected_option):
        print(f"Setting applied: {selected_option}")
        print(f"Value: {settings.get_settings()[selected_option]}")
        events.on_setting_change(selected_option)

    def close_window(self):
        print("Closing window")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnsemblerGUI(root)
    root.mainloop()
