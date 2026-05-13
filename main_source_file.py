import threading
import hashlib
import os
import shutil
import time
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog, messagebox, ttk
selected_folder = ""
log_file = "undo_log.txt"
auto_organizing = False


file_types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx"],
    "Music": [".mp3", ".wav"],
    "Zip_Files": [".zip", ".rar"],
    "Python_Files": [".py"]
}

stats = {
    "Images": 0,
    "Videos": 0,
    "Documents": 0,
    "Music": 0,
    "Zip_Files": 0,
    "Python_Files": 0,
    "Others": 0
}

seen_files = {}


# Select folder
def select_folder():
    global selected_folder

    selected_folder = filedialog.askdirectory()

    if selected_folder:
        folder_label.config(text=f"Selected Folder:\n{selected_folder}")

# Drag & Drop Function
def drop(event):

    global selected_folder

    # Get dropped folder path
    selected_folder = event.data.strip("{}")

    # Show folder path on screen
    folder_label.config(
        text=f"Selected Folder:\n{selected_folder}"
    )

# Generate file hash
def get_file_hash(file_path):

    hasher = hashlib.md5()

    with open(file_path, "rb") as file:

        while chunk := file.read(4096):

            hasher.update(chunk)

    return hasher.hexdigest()

# Organize files
def organize_files(show_message=True):

    global stats

    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
        return

    # Reset statistics
    stats = {
        "Images": 0,
        "Videos": 0,
        "Documents": 0,
        "Music": 0,
        "Zip_Files": 0,
        "Python_Files": 0,
        "Others": 0
    }

    seen_files.clear()

    open(log_file, "w").close()
    files = [
        file for file in os.listdir(selected_folder)
        if os.path.isfile(os.path.join(selected_folder, file))
    ]

    total_files = len(files)

    if total_files == 0:
        messagebox.showinfo("Info", "No files found!")
        return

    progress["value"] = 0
    progress["maximum"] = total_files


    

    for index, file in enumerate(files, start=1):

        file_path = os.path.join(selected_folder, file)

        if os.path.isdir(file_path):
            continue

        extension = os.path.splitext(file)[1].lower()
        # Duplicate check
        file_hash = get_file_hash(file_path)
        
        if file_hash in seen_files:
            activity_log.insert(
                tk.END,
                f"Duplicate Found: {file}\n"
            )
            
            activity_log.see(tk.END)
            
            continue
        
        else:
            seen_files[file_hash] = file_path

        moved = False

        for folder, extensions in file_types.items():

            if extension in extensions:

                folder_path = os.path.join(selected_folder, folder)

                os.makedirs(folder_path, exist_ok=True)

                destination = os.path.join(folder_path, file)

                with open(log_file, "a") as log:
                    log.write(f"{file_path}|{destination}\n")

                shutil.move(file_path, destination)

                stats[folder] += 1

                activity_log.insert(
                     tk.END,
                     f"Moved {file} → {folder}\n"
                )
                
                activity_log.see(tk.END)
                
                progress["value"] = index
                root.update_idletasks()
                time.sleep(0.1)

                moved = True
                break

        if not moved:

            others_folder = os.path.join(selected_folder, "Others")

            os.makedirs(others_folder, exist_ok=True)

            destination = os.path.join(others_folder, file)

            with open(log_file, "a") as log:
                log.write(f"{file_path}|{destination}\n")

            shutil.move(file_path, destination)

            stats["Others"] += 1

            activity_log.insert(
                tk.END,
                f"Moved {file} → Others\n"
            )

            activity_log.see(tk.END)

            progress["value"] = index
            root.update_idletasks()

    # Update statistics text
    stats_text = "Files Organized:\n"

    for category, count in stats.items():
        stats_text += f"{category}: {count}\n"

    stats_label.config(text=stats_text)

    if show_message:
        messagebox.showinfo(
            "Success",
            "Files organized successfully!"
        )




# Undo changes
def undo_changes():

    if not os.path.exists(log_file):
        messagebox.showerror("Error", "No undo log found!")
        return

    with open(log_file, "r") as log:
        lines = log.readlines()

    for line in reversed(lines):

        source, destination = line.strip().split("|")

        if os.path.exists(destination):

            shutil.move(destination, source)

    messagebox.showinfo("Undo", "Files restored successfully!")

# Auto Organize Function
# Auto Organize Function
# Auto Organize Function
def auto_organize():

    global auto_organizing

    while auto_organizing:
        
        root.after(
            0,
            lambda: activity_log.insert(
                tk.END,
                "Auto organizer checking...\n"
            )
        )

        root.after(
            0,
            lambda: activity_log.see(tk.END)
        )

        if selected_folder:

            try:
                organize_files(False)

            except Exception as e:

                print(e)

        time.sleep(5)

# Start Auto Organizing
def start_auto_organize():

    global auto_organizing

    if auto_organizing:
        return

    auto_organizing = True
    status_label.config(
        text="🟢 Auto Organizer Running",
        fg="lightgreen"
    )

    messagebox.showinfo(
        "Auto Organizer",
        "Auto organizing started!"
    )

# Stop Auto Organizing
def stop_auto_organize():

    global auto_organizing

    auto_organizing = False
    status_label.config(
        text="🔴 Auto Organizer Stopped",
        fg="orange"
    )

    messagebox.showinfo(
        "Auto Organizer",
        "Auto organizing stopped!"
    )

# GUI Window
from tkinterdnd2 import TkinterDnD

root = TkinterDnD.Tk()
root.title("Smart File Organizer")
root.geometry("700x600")
root.configure(bg="#1e1e1e")

# Title
title = tk.Label(
    root,
    text="Smart File Organizer",
    font=("Arial", 20, "bold"),
    bg="#1e1e1e",
    fg="white"
)
title.pack(pady=20)

# Folder Label
folder_label = tk.Label(
    root,
    text="Drag & Drop Folder Here\nor Click 'Select Folder'",
    wraplength=450,
    bg="#2b2b2b",
    fg="lightgray",
    font=("Arial", 11),
    relief="ridge",
    bd=2,
    padx=20,
    pady=20
)
folder_label.pack(pady=10)

folder_label.drop_target_register('DND_Files')

folder_label.dnd_bind('<<Drop>>', drop)

# Button Style
button_style = {
    "font": ("Arial", 12),
    "bg": "#333333",
    "fg": "white",
    "activebackground": "#555555",
    "activeforeground": "white",
    "width": 20,
    "bd": 0,
    "pady": 8
}

# Buttons
select_btn = tk.Button(
    root,
    text="Select Folder",
    command=select_folder,
    **button_style
)
select_btn.pack(pady=10)

organize_btn = tk.Button(
    root,
    text="Organize Files",
    command=organize_files,
    **button_style
)
organize_btn.pack(pady=10)

undo_btn = tk.Button(
    root,
    text="Undo Changes",
    command=undo_changes,
    **button_style
)
undo_btn.pack(pady=10)

start_auto_btn = tk.Button(
    root,
    text="Start Auto Organize",
    command=start_auto_organize,
    **button_style
)

start_auto_btn.pack(pady=10)


stop_auto_btn = tk.Button(
    root,
    text="Stop Auto Organize",
    command=stop_auto_organize,
    **button_style
)

stop_auto_btn.pack(pady=10) 

stats_label = tk.Label(
    root,
    text="No statistics yet",
    bg="#1e1e1e",
    fg="lightgreen",
    font=("Arial", 10),
    justify="left"
)

stats_label.pack(pady=15)

status_label = tk.Label(
    root,
    text="🔴 Auto Organizer Stopped",
    bg="#1e1e1e",
    fg="orange",
    font=("Arial", 11, "bold")
)


progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=400,
    mode="determinate"
)

progress.pack(pady=10)

activity_log = scrolledtext.ScrolledText(
    root,
    width=60,
    height=8,
    bg="#2b2b2b",
    fg="lightgreen",
    font=("Consolas", 9)
)

activity_log.pack(pady=10)

auto_thread = threading.Thread(
    target=auto_organize,
    daemon=True
)

auto_thread.start()

root.mainloop()