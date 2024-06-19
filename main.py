
import subprocess
import re
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import tkinter as tk
from tkinter import PhotoImage
import json
import os


ext_name_list = []
ext_id_list = []
ext_version_list = []
username = os.getlogin()


def extract_keywords(text):
    pattern = "__MSG_(.*?)__"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None


def get_localized_name(extension_path, placeholder):
    # placeholder_key = "test"
    if placeholder.startswith("__MSG_"):
        placeholder_key = extract_keywords(placeholder)

        default_lang = "en"
        locales_path = os.path.join(
            extension_path, "_locales", default_lang, "messages.json")
        if os.path.isfile(locales_path):
            try:
                with open(locales_path, 'r') as file:
                    messages = json.load(file)
                    return messages.get(placeholder_key, {}).get("message", placeholder)
            except json.JSONDecodeError as e:
                print(f"Error loading JSON file {locales_path}: {e}")
                return placeholder
    # print(placeholder_key)
    return placeholder


def display_icon(event):
    selected_index = extensions_combobox.current()
    if selected_index != -1:
        ext_name = extensions_combobox.get()
        icon_path = extensions_icons[selected_index]
        try:
            image = Image.open(icon_path)
            image = image.resize((64, 64), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            icon_label.configure(image=photo)
            icon_label.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")


def list_extensions():
    directory = "/Users/{}/Library/Application Support/Google/Chrome/Default/Extensions".format(
        username)
    try:
        for widget in extensions_frame.winfo_children():
            widget.destroy()

        global extensions_icons
        extensions_icons = []
        extensions = []
        for ext_id in os.listdir(directory):
            ext_path = os.path.join(directory, ext_id)
            if os.path.isdir(ext_path):
                for version in os.listdir(ext_path):
                    manifest_path = os.path.join(
                        ext_path, version, "manifest.json")
                    if os.path.isfile(manifest_path):
                        with open(manifest_path, 'r') as manifest_file:
                            manifest_data = json.load(manifest_file)
                            ext_name = manifest_data.get('name', 'Unknown')
                            ext_name = get_localized_name(
                                os.path.join(ext_path, version), ext_name)
                            icon_path = manifest_data.get(
                                'icons', {}).get('128', '')
                            if icon_path:
                                icon_path = os.path.join(
                                    ext_path, version, icon_path)
                                extensions_icons.append(icon_path)
                                extensions.append(ext_name)
                            ext_name_list.append(ext_name)
                            ext_id_list.append(ext_id)
                            ext_version_list.append(version)

        extensions_combobox['values'] = extensions

    except FileNotFoundError:
        messagebox.showerror("Error", "Directory not found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def return_index(target):
    if target in ext_name_list:
        index = ext_name_list.index(target)
        return index
    raise ValueError("'{}' is not in the list".format(target))


def execute_command():
    ext_name = extensions_combobox.get()
    i = int(return_index(ext_name))
    ext_id = ext_id_list[i]
    ext_version = ext_version_list[i]

    command = "xcrun safari-web-extension-converter /Users/{}/Library/Application\ Support/Google/Chrome/Default/Extensions/{}/{}".format(
        username, ext_id, ext_version)
    try:
        print("starting")
        print(ext_name, " ", ext_id, " ", ext_version)
        subprocess.run(command, shell=True)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))


root = tk.Tk()

root.title("C2S Extension Converter")
root.geometry("600x320")
icon = PhotoImage(file='plug.png')
root.iconphoto(True, icon)
root.resizable(False, False)
center_window(root, 600, 320)


list_button = tk.Button(
    root, text="Refresh list", command=list_extensions, width=10, height=2)
list_button.pack(pady=25)

extensions_combobox = ttk.Combobox(root, width=30)
extensions_combobox.pack(pady=0)
extensions_combobox.pack(padx=27)
extensions_combobox.bind("<<ComboboxSelected>>", display_icon)

icon_frame = tk.Frame(root)
icon_frame.pack(pady=(25, 20))
icon_label = tk.Label(icon_frame)
icon_label.pack()

extensions_frame = tk.Frame(root)
extensions_frame.pack(padx=0, pady=0)

# Add a button to execute a command
execute_button = tk.Button(
    root, text="Convert", command=execute_command, width=10, height=2)
execute_button.pack(pady=(0, 40))

root.mainloop()
