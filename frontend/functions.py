from tkinter import Toplevel, Label, Entry, Button


def create_project_window(parent):

    project_window = Toplevel(parent)

    # ---------------- WINDOW ----------------

    project_window.title("Create New Project")
    project_window.geometry("400x240")
    project_window.resizable(False, False)

    # Dark theme
    project_window.configure(bg="#15181D")

    # ---------------- CENTER WINDOW ----------------

    parent.update_idletasks()

    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()

    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    window_width = 400
    window_height = 240

    x = parent_x + (parent_width - window_width) // 2
    y = parent_y + (parent_height - window_height) // 2

    project_window.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )

    # Keep dialog above main window
    project_window.transient(parent)

    # Prevent clicking the main window while dialog is open
    project_window.grab_set()

    # ---------------- TITLE ----------------

    title = Label(
        project_window,
        text="Create New Project",
        font=("Segoe UI", 18, "bold"),
        fg="#FFFFFF",
        bg="#15181D"
    )

    title.pack(pady=(25, 10))

    # ---------------- INSTRUCTION ----------------

    instruction = Label(
        project_window,
        text="Enter a name for your project:",
        font=("Segoe UI", 11),
        fg="#A9AFB8",
        bg="#15181D"
    )

    instruction.pack()

    # ---------------- PROJECT NAME ----------------

    project_name = Entry(
        project_window,
        font=("Segoe UI", 12),
        width=30,
        fg="#FFFFFF",
        bg="#20242A",
        insertbackground="#FFFFFF",
        relief="flat"
    )

    project_name.pack(
        pady=(12, 15),
        ipady=7
    )

    # Automatically put cursor inside entry
    project_name.focus_set()

    # ---------------- CREATE BUTTON ----------------

    create_button = Button(
        project_window,
        text="Create",
        font=("Segoe UI", 11, "bold"),
        fg="#FFFFFF",
        bg="#2563EB",
        activeforeground="#FFFFFF",
        activebackground="#1D4ED8",
        relief="flat",
        cursor="hand2",
        padx=22,
        pady=7
    )

    create_button.pack()


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
