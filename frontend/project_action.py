import tkinter as tk

from assets import asset_path


BG = "#080D17"
PANEL = "#101722"
BORDER = "#263242"
TEXT = "#F4F7FB"
MUTED = "#AEB7C5"
BLUE = "#1769E8"


def create_project_action_window(parent, project, on_back=None):
    """Show the actions available immediately after creating a project."""
    action_window = tk.Toplevel(parent)
    action_window.title("Project Created")
    action_window.geometry("540x505")
    action_window.minsize(500, 470)
    action_window.configure(bg=BG)
    action_window.transient(parent)

    content = tk.Frame(action_window, bg=BG)
    content.pack(fill="both", expand=True, padx=30, pady=20)

    back_button = tk.Button(
        content,
        text="<-  Back to Projects",
        font=("Segoe UI", 9),
        fg="#4A99FF",
        bg=BG,
        activeforeground="#78B3FF",
        activebackground=BG,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=lambda: close_action_window(),
    )
    back_button.pack(anchor="w")

    tk.Label(content, text="✓", font=("Segoe UI", 24, "bold"), fg="#07130B", bg="#4CCB76", width=2, height=1).pack(pady=(12, 7))
    tk.Label(content, text="Project Created Successfully!", font=("Segoe UI", 15, "bold"), fg=TEXT, bg=BG).pack()
    tk.Label(content, text="Your project is ready. What would you like to do next?", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(pady=(3, 14))

    project_panel = tk.Frame(content, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    project_panel.pack(fill="x", ipady=12)

    folder_image = tk.PhotoImage(file=asset_path("foldericon.png")).subsample(11, 11)
    folder_label = tk.Label(project_panel, image=folder_image, bg=PANEL)
    folder_label.image = folder_image
    folder_label.pack(side="left", padx=(16, 14))

    project_details = tk.Frame(project_panel, bg=PANEL)
    project_details.pack(side="left", anchor="center")
    tk.Label(project_details, text=project.get("name", "Untitled Project"), font=("Segoe UI", 12, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w")
    tk.Label(project_details, text=f"{project.get('question_count', 0)} Questions    |    Created just now", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(4, 0))

    tk.Label(content, text="Choose an action", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(14, 7))

    actions = tk.Frame(content, bg=BG)
    actions.pack(fill="x")
    actions.grid_columnconfigure(0, weight=1)
    actions.grid_columnconfigure(1, weight=1)

    _create_action_card(actions, 0, "▣", "Create OMR", "Generate OMR sheet for\nthis project.", "Create OMR")
    _create_action_card(actions, 1, "⌕", "Upload Answer Key", "Upload the correct answer\nkey (CSV) for this project.", "Upload Answer Key")

    tip = tk.Frame(content, bg="#0B1423", highlightbackground=BORDER, highlightthickness=1)
    tip.pack(fill="x", pady=(12, 0), ipady=7)
    tk.Label(tip, text="i", font=("Segoe UI", 9, "bold"), fg="#3C8BFF", bg="#0B1423").pack(side="left", padx=(11, 8))
    tk.Label(tip, text="Tip: You can always perform these actions later from the project details page.", font=("Segoe UI", 8), fg=MUTED, bg="#0B1423").pack(side="left")

    def close_action_window():
        action_window.destroy()
        if on_back is not None:
            on_back()

    action_window.protocol("WM_DELETE_WINDOW", close_action_window)
    return action_window


def _create_action_card(parent, column, icon, title, description, button_text):
    card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    card.grid(row=0, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
    tk.Label(card, text=icon, font=("Segoe UI", 22, "bold"), fg="#DCEAFF", bg="#173B78", width=2, height=1).pack(pady=(10, 7))
    tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL).pack()
    tk.Label(card, text=description, font=("Segoe UI", 8), fg=MUTED, bg=PANEL, justify="center").pack(pady=(4, 10))
    tk.Button(card, text=button_text, font=("Segoe UI", 9, "bold"), fg="white", bg=BLUE, activebackground="#2B7CF0", activeforeground="white", relief="flat", bd=0, padx=13, pady=5, cursor="hand2").pack(pady=(0, 10))