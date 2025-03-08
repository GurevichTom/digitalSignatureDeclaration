"""
GUI Application for Digital Signature Declaration

Provides a Tkinter-based interface to prompt the user for name, ID, gender, and
the PDF to sign. Relies on the sign_declaration function from signing.py to perform
the underlying PDF manipulation.

Usage:
    python main.py

Note:
    This script is environment-specific and may rely on custom icons or images
    that need to be set in resource_path or config.py.
"""

import io
import json
import os
import os.path
import subprocess
import sys
from datetime import date

import PyPDF2
from PIL import Image
from pdf2image import convert_from_path
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from digitalSignatureDeclaration import sign_declaration, detect_declaration_type
from config import icon_path


def load_data():
    if os.path.exists("app_data.json"):
        with open("app_data.json", "r") as file:
            return json.load(file)
    return {}


def save_data(name, id, gender, output_folder):
    data = {"name": name, "id": id, "gender": gender, "output_folder": output_folder}
    with open("app_data.json", "w") as file:
        json.dump(data, file)



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(".", "..", "digitalSignatureDeclaration"))

    return os.path.join(base_path, relative_path)


def main():
    """
        Launches the Tkinter GUI for signing PDF declarations.

        Steps:
        1. Loads user preferences from local JSON (app_data.json).
        2. Provides inputs for name, ID, gender, and file selection.
        3. Calls sign_declaration(...) once the user selects 'Begin'.
        4. Spawns a new process to open the signed PDF upon completion.
        """

    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    # Load data
    data = load_data()

    # Variables that will be accessed and modified by inner functions
    file_path = None
    output_folder = data.get("output_folder", "")  # Loading saved data

    # GUI code
    root = tk.Tk()
    root.title("Sign Declaration")

    # Set the icon for the window
    root.tk.call('wm', 'iconbitmap', root._w, icon_path())

    # Set the title of the window
    root.title("SignMyDoc")

    # Name label and entry
    label_name = ttk.Label(root, text="Name:")
    label_name.pack()
    entry_name = ttk.Entry(root)
    entry_name.pack()
    entry_name.insert(0, data.get("name", ""))  # Loading saved data

    # ID label and entry
    label_id = ttk.Label(root, text="ID:")
    label_id.pack()
    entry_id = ttk.Entry(root)
    entry_id.pack()
    entry_id.insert(0, data.get("id", ""))  # Loading saved data

    # Declaration type radio buttons
    radio_declaration_type_var = tk.StringVar(value="person")
    radio_company = ttk.Radiobutton(root, text="Company", variable=radio_declaration_type_var, value="company")
    radio_person = ttk.Radiobutton(root, text="Person", variable=radio_declaration_type_var, value="person")
    radio_company.pack()
    radio_person.pack()

    # Gender radio buttons
    radio_gender_var = tk.StringVar(value=data.get("gender", ""))  # Loading saved data
    label_gender = ttk.Label(root, text="Gender:")
    label_gender.pack()
    radio_male = ttk.Radiobutton(root, text="Male", variable=radio_gender_var, value='male')
    radio_male.pack()
    radio_female = ttk.Radiobutton(root, text="Female", variable=radio_gender_var, value='female')
    radio_female.pack()

    # Function to ask user for file
    def ask_for_file():
        nonlocal file_path  # Declare file_path as nonlocal to modify it
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            declaration_type = detect_declaration_type(file_path)
            radio_declaration_type_var.set(declaration_type)
            root.update_idletasks()

    # Function to ask user for folder
    def ask_for_folder():
        nonlocal output_folder  # Declare output_folder as nonlocal to modify it
        output_folder = filedialog.askdirectory()

    # The function that gets executed when the user presses the "Begin" button
    def on_begin_button():
        name = entry_name.get()
        id = entry_id.get()
        declaration_type = radio_declaration_type_var.get()
        declarator_gender = radio_gender_var.get()

        if not name or not id or not file_path or not output_folder or not declaration_type or not declarator_gender:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            # Saving data
            save_data(name, id, declarator_gender, output_folder)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        output_pdf_path = sign_declaration(name, id, file_path, output_folder, declaration_type, declarator_gender)
        subprocess.Popen([output_pdf_path], shell=True)
        messagebox.showinfo("Info", "Process completed")

    # Buttons to select file and folder
    button_select_file = ttk.Button(root, text="Select Declaration File", command=ask_for_file)
    button_select_file.pack()

    button_select_folder = ttk.Button(root, text="Select Output Folder", command=ask_for_folder)
    button_select_folder.pack()

    # Button to start the process
    button_begin = ttk.Button(root, text="Begin", command=on_begin_button)
    button_begin.pack()

    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
