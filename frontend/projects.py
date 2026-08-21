import tkinter as tk


def create_projects_page(window):
    # Main Projects page
    projects_page = tk.Frame(
        window,
        bg="black"
    )

    # Page title
    title = tk.Label(
        projects_page,
        text="Projects",
        font=("Segoe UI", 26, "bold"),
        fg="white",
        bg="black"
    )
    title.place(x=60, y=50)

    # Subtitle
    subtitle = tk.Label(
        projects_page,
        text="View and manage your OMR projects.",
        font=("Segoe UI", 14),
        fg="#A7A7A7",
        bg="black"
    )
    subtitle.place(x=62, y=95)

    return projects_page