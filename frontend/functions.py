
from tkinter import Toplevel, Label, Entry, Button


def create_project_window(parent):    #create a new window for creating a project

    project_window = Toplevel(parent)

    project_window.title("Create New Project")   #set the title of the window
    project_window.geometry("400x220")
    project_window.resizable(False, False)

    title = Label(                # added a label for the project window title
        project_window,
        text="Create New Project",
        font=("Segoe UI", 18, "bold")
    )
    title.pack(pady=(25, 10))    

    instruction = Label(         #created a label for the project window instruction
        project_window,
        text="Enter a name for your project:",
        font=("Segoe UI", 11)
    )
    instruction.pack()

    project_name = Entry(    #created an entry widget for the user to input the project name
        project_window,
        font=("Segoe UI", 12),
        width=30
    )
    project_name.pack(pady=10)

    create_button = Button(       #created a button to create the project
        project_window,
        text="Create",
        font=("Segoe UI", 11, "bold")
    )
    create_button.pack(pady=5)


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
