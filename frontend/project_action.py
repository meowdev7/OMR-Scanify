import tkinter as tk
from datetime import datetime, timezone
from tkinter import filedialog, messagebox
import csv
import requests
from storage import get_project, update_answer_key

from assets import asset_path


BG = "#080D17"
PANEL = "#101722"
BORDER = "#263242"
TEXT = "#F4F7FB"
MUTED = "#AEB7C5"
BLUE = "#1769E8"


def format_relative_creation_date(value, now=None):
    if not value:
        return "Created date unavailable"

    try:
        created_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if created_at.year == 1:
            return "Created date unavailable"
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        current_time = now or datetime.now(timezone.utc)
        elapsed_seconds = max(0, (current_time - created_at).total_seconds())
    except (AttributeError, TypeError, ValueError):
        return "Created date unavailable"

    if elapsed_seconds < 60:
        return "Created just now"

    elapsed_days = int(elapsed_seconds // 86400)
    if elapsed_days < 7:
        return f"Created {elapsed_days} day{'s' if elapsed_days != 1 else ''} ago"

    elapsed_weeks = elapsed_days // 7
    return f"Created {elapsed_weeks} week{'s' if elapsed_weeks != 1 else ''} ago"


def parse_answer_key_csv(rows, expected_count):
    rows = [row for row in rows if row]
    if not rows:
        raise ValueError("The CSV file is empty.")

    header = [cell.strip().casefold() for cell in rows[0]]
    has_header = header == ["question", "answer"]
    if has_header:
        rows = rows[1:]

    answers = []
    for row_number, row in enumerate(rows, start=2 if has_header else 1):
        if any(not cell.strip() for cell in row):
            raise ValueError(f"Row {row_number} contains a blank value.")
        if len(row) != (2 if has_header else 1):
            raise ValueError(f"Row {row_number} must contain {'question and answer' if has_header else 'one answer'}.")

        answer = row[1] if has_header else row[0]
        answer = answer.strip().upper()
        if answer not in {"A", "B", "C", "D"}:
            raise ValueError(f"Row {row_number} has invalid answer '{answer}'. Use A, B, C, or D.")
        answers.append(answer)

    if len(answers) != expected_count:
        raise ValueError(f"Expected {expected_count} answers, found {len(answers)}.")
    return answers


def create_project_action_window(parent, project, on_back=None, on_create_omr=None, on_project_updated=None):
    """Show the actions available immediately after creating a project."""
    action_window = tk.Frame(parent, bg=BG)

    content = tk.Frame(action_window, bg=BG)
    content.pack(fill="both", expand=True, padx=30, pady=20)

    def close_action_window():
        action_window.pack_forget()
        if on_back is not None:
            on_back()

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
        command=close_action_window,
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
    tk.Label(project_details, text=f"{project.get('question_count', 0)} Questions    |    {format_relative_creation_date(project.get('created_at'))}", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(4, 0))

    tk.Label(content, text="Choose an action", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(14, 7))

    actions = tk.Frame(content, bg=BG)
    actions.pack(fill="x")
    actions.grid_columnconfigure(0, weight=1)
    actions.grid_columnconfigure(1, weight=1)

    _create_action_card(actions, 0, "▣", "Create OMR", "Generate OMR sheet for\nthis project.", "Create OMR", on_create_omr)
    def upload_answer_key():
        filename = filedialog.askopenfilename(parent=action_window.winfo_toplevel(), filetypes=(("CSV files", "*.csv"),))
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                answers = parse_answer_key_csv(list(csv.reader(file)), project.get("question_count", 0))
            update_answer_key(project["id"], answers)
            updated_project = get_project(project["id"])
            messagebox.showinfo("Answer key uploaded", "The answer key was saved to the backend.", parent=action_window.winfo_toplevel())
            if on_project_updated is not None:
                on_project_updated(updated_project)
        except (OSError, ValueError, KeyError, requests.RequestException) as error:
            messagebox.showerror("Answer key upload failed", str(error), parent=action_window.winfo_toplevel())

    _create_action_card(actions, 1, "⌕", "Upload Answer Key", "Upload the correct answer\nkey (CSV) for this project.", "Upload Answer Key", upload_answer_key)

    answer_key_panel = tk.Frame(content, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    answer_key_panel.pack(fill="both", expand=True, pady=(12, 0), ipady=10)
    tk.Label(answer_key_panel, text="Answer Key", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=16)
    answer_key = project.get("answer_key") or []
    if answer_key:
        key_text = "    ".join(f"{index}: {answer}" for index, answer in enumerate(answer_key, start=1))
        tk.Label(answer_key_panel, text=key_text, font=("Consolas", 10), fg=MUTED, bg=PANEL, wraplength=900, justify="left").pack(anchor="w", padx=16, pady=(8, 0))
    else:
        tk.Label(answer_key_panel, text="No answer key uploaded yet.", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(8, 0))

    tip = tk.Frame(content, bg="#0B1423", highlightbackground=BORDER, highlightthickness=1)
    tip.pack(fill="x", pady=(12, 0), ipady=7)
    tk.Label(tip, text="i", font=("Segoe UI", 9, "bold"), fg="#3C8BFF", bg="#0B1423").pack(side="left", padx=(11, 8))
    tk.Label(tip, text="Tip: You can always perform these actions later from the project details page.", font=("Segoe UI", 8), fg=MUTED, bg="#0B1423").pack(side="left")

    return action_window


def _create_action_card(parent, column, icon, title, description, button_text, command=None):
    card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    card.grid(row=0, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
    tk.Label(card, text=icon, font=("Segoe UI", 22, "bold"), fg="#DCEAFF", bg="#173B78", width=2, height=1).pack(pady=(10, 7))
    tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL).pack()
    tk.Label(card, text=description, font=("Segoe UI", 8), fg=MUTED, bg=PANEL, justify="center").pack(pady=(4, 10))
    tk.Button(card, text=button_text, command=command, font=("Segoe UI", 9, "bold"), fg="white", bg=BLUE, activebackground="#2B7CF0", activeforeground="white", relief="flat", bd=0, padx=13, pady=5, cursor="hand2").pack(pady=(0, 10))