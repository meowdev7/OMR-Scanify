from tkinter import Toplevel, Label, Entry, Button

import requests


def create_project(project_window, project_name, question_count):
    data = {
        "name": project_name,
        "question_count": int(question_count)
    }

    response = requests.post(
        "http://127.0.0.1:8080/api/v1/projects",
        json=data
    )

    print("Status:", response.status_code)
    print("Response:", response.json())


def create_project_window(parent):

    project_window = Toplevel(parent)

    project_window.title("Create New Project")
    project_window.geometry("400x280")
    project_window.resizable(False, False)

    # Make the dialog appear centered relative to the main window
    parent.update_idletasks()

    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    window_width = 400
    window_height = 280

    x = parent_x + (parent_width - window_width) // 2
    y = parent_y + (parent_height - window_height) // 2

    project_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Dark theme
    project_window.config(bg="#15181D")

    # Title
    title = Label(
        project_window,
        text="Create New Project",
        font=("Segoe UI", 18, "bold"),
        fg="#FFFFFF",
        bg="#15181D"
    )
    title.pack(pady=(25, 10))

    # Project name label
    instruction = Label(
        project_window,
        text="Enter project name:",
        font=("Segoe UI", 11),
        fg="#A9AFB8",
        bg="#15181D"
    )
    instruction.pack()

    # Project name input
    project_name = Entry(
        project_window,
        font=("Segoe UI", 12),
        width=30,
        bg="#22272E",
        fg="#FFFFFF",
        insertbackground="#FFFFFF"
    )
    project_name.pack(pady=10)

    # Question count
    question_label = Label(
        project_window,
        text="Number of questions:",
        font=("Segoe UI", 11),
        fg="#A9AFB8",
        bg="#15181D"
    )
    question_label.pack()

    question_count = Entry(
        project_window,
        font=("Segoe UI", 12),
        width=30,
        bg="#22272E",
        fg="#FFFFFF",
        insertbackground="#FFFFFF"
    )
    question_count.pack(pady=10)

    # Create button
    create_button = Button(
    project_window,
    text="Create",
    font=("Segoe UI", 11, "bold"),
    command=lambda: create_project(
        project_window,
        project_name.get(),
        question_count.get()
    )
)
    create_button.pack(pady=5)

    # Keep dialog above main window
    project_window.transient(parent)
    project_name.focus()

    
def card_enter(event):       #change the background color of the project card when the mouse enters the card area
    quick_scan_card.config(bg="#1C2128")
    card_title.config(bg="#1C2128")
    card_subtitle.config(bg="#1C2128")
    card_image_label.config(bg="#1C2128")


def card_leave(event):  #change the background color of the project card back to the original color when the mouse leaves the card area
    quick_scan_card.config(bg="#15181D")
    card_title.config(bg="#15181D")
    card_subtitle.config(bg="#15181D")
    card_image_label.config(bg="#15181D")
