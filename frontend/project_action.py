import tkinter as tk
from datetime import datetime, timezone
from tkinter import filedialog, messagebox
import csv
import requests
from storage import export_results, get_project, import_students, update_answer_key
from answer_key import answer_key_menu, open_answer_key_editor

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

    def refresh_project_view():
        nonlocal project
        try:
            project = get_project(project["id"])
        except (KeyError, requests.RequestException):
            return
        if on_project_updated is not None:
            on_project_updated(project)

    def update_answer_key_panel():
        for child in answer_key_panel.winfo_children():
            child.destroy()

        heading = tk.Frame(answer_key_panel, bg=PANEL)
        heading.pack(fill="x", padx=16)
        tk.Label(heading, text="Answer Key", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL).pack(side="left")
        answer_key = project.get("answer_key") or []
        if answer_key:
            menu = answer_key_menu(answer_key_panel, project, lambda: (refresh_project_view(), update_answer_key_panel()))
            tk.Button(heading, text="...", command=lambda: menu.post(heading.winfo_rootx() + heading.winfo_width() - 12, heading.winfo_rooty() + heading.winfo_height()), font=("Segoe UI", 10, "bold"), fg=MUTED, bg=PANEL, activebackground="#172338", activeforeground=TEXT, relief="flat", bd=0, width=3).pack(side="right")
            key_text = "    ".join(f"{index}: {answer}" for index, answer in enumerate(answer_key, start=1))
            tk.Label(answer_key_panel, text=key_text, font=("Consolas", 10), fg=MUTED, bg=PANEL, wraplength=900, justify="left").pack(anchor="w", padx=16, pady=(8, 0))
        else:
            tk.Label(answer_key_panel, text="No answer key uploaded yet.", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(8, 0))

    def update_student_and_result_panels():
        for child in student_summary_panel.winfo_children():
            child.destroy()
        for child in result_summary_panel.winfo_children():
            child.destroy()

        students = project.get("students") or []
        results = []
        try:
            results = get_project(project["id"]).get("results") or []
        except Exception:
            results = []

        tk.Label(student_summary_panel, text="Students", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=16, pady=(14, 8))
        if students:
            for student in students[:6]:
                labels = [student.get("name") or "Unnamed student", student.get("sheet_id") or "No sheet ID"]
                tk.Label(student_summary_panel, text=f"• {labels[0]} ({labels[1]})", font=("Segoe UI", 9), fg=MUTED, bg=PANEL, justify="left", anchor="w").pack(anchor="w", padx=16, pady=2)
            if len(students) > 6:
                tk.Label(student_summary_panel, text=f"+ {len(students) - 6} more students", font=("Segoe UI", 8), fg="#4A99FF", bg=PANEL).pack(anchor="w", padx=16, pady=(4, 0))
        else:
            tk.Label(student_summary_panel, text="No students imported yet.", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(6, 10))

        tk.Label(result_summary_panel, text="Recent Results", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=16, pady=(14, 8))
        if results:
            for result in results[:6]:
                tk.Label(result_summary_panel, text=f"• {result.get('student_name', 'Unknown')} — {result.get('marks', 0)}/{result.get('total_questions', 0)}", font=("Segoe UI", 9), fg=MUTED, bg=PANEL, justify="left", anchor="w").pack(anchor="w", padx=16, pady=2)
            if len(results) > 6:
                tk.Label(result_summary_panel, text=f"+ {len(results) - 6} more results", font=("Segoe UI", 8), fg="#4A99FF", bg=PANEL).pack(anchor="w", padx=16, pady=(4, 0))
        else:
            tk.Label(result_summary_panel, text="No scanned submissions yet.", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(6, 10))

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
    actions.pack(fill="both", expand=True)
    actions.grid_columnconfigure(0, weight=1)
    actions.grid_columnconfigure(1, weight=1)
    actions.grid_rowconfigure(0, weight=1)
    actions.grid_rowconfigure(1, weight=1)

    def upload_answer_key():
        filename = filedialog.askopenfilename(parent=action_window.winfo_toplevel(), filetypes=(("CSV files", "*.csv"),))
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                answers = parse_answer_key_csv(list(csv.reader(file)), project.get("question_count", 0))
            update_answer_key(project["id"], answers)
            refresh_project_view()
            update_answer_key_panel()
            update_student_and_result_panels()
            messagebox.showinfo("Answer key uploaded", "The answer key was saved to the backend.", parent=action_window.winfo_toplevel())
            if on_project_updated is not None:
                on_project_updated(project)
        except (OSError, ValueError, KeyError, requests.RequestException) as error:
            messagebox.showerror("Answer key upload failed", str(error), parent=action_window.winfo_toplevel())

    def create_answer_key():
        open_answer_key_editor(action_window, project, lambda: (refresh_project_view(), update_answer_key_panel(), on_project_updated(project) if on_project_updated else None))

    def import_students_csv():
        filename = filedialog.askopenfilename(parent=action_window.winfo_toplevel(), filetypes=(("CSV files", "*.csv"),))
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                csv_text = file.read()
            imported = import_students(project["id"], csv_text)
            refresh_project_view()
            update_student_and_result_panels()
            messagebox.showinfo("Students imported", f"{len(imported)} student(s) were imported successfully.", parent=action_window.winfo_toplevel())
            if on_project_updated is not None:
                on_project_updated(project)
        except (OSError, ValueError, KeyError, requests.RequestException) as error:
            messagebox.showerror("Student import failed", str(error), parent=action_window.winfo_toplevel())

    def export_results_csv():
        if not project.get("id"):
            return
        filename = filedialog.asksaveasfilename(
            parent=action_window.winfo_toplevel(),
            title="Export results",
            defaultextension=".csv",
            initialfile=f"{project.get('name', 'project')}_results.csv",
            filetypes=(("CSV files", "*.csv"),),
        )
        if not filename:
            return
        try:
            export_results(project["id"], filename)
            messagebox.showinfo("Results exported", f"The results were saved to:\n{filename}", parent=action_window.winfo_toplevel())
        except (OSError, requests.RequestException) as error:
            messagebox.showerror("Export failed", str(error), parent=action_window.winfo_toplevel())

    actions.grid_rowconfigure(2, weight=1)
    _create_action_card(actions, 0, 0, "▣", "Create OMR", "Generate OMR sheet for\nthis project.", "Create OMR", on_create_omr)
    _create_action_card(actions, 0, 1, "⇩", "Import Students", "Bring in student records\nfrom a CSV file.", "Import Students", import_students_csv)
    _create_action_card(actions, 1, 0, "✎", "Create Answer Key", "Fill the answer key\nwith the OMR layout.", "Create Answer Key", create_answer_key)
    _create_action_card(actions, 1, 1, "⌕", "Upload Answer Key", "Upload the correct answer\nkey (CSV) for this project.", "Upload Answer Key", upload_answer_key)
    _create_action_card(actions, 2, 0, "⤓", "Export Results", "Download the project score report\nas CSV.", "Export Results", export_results_csv)

    overview = tk.Frame(content, bg=BG)
    overview.pack(fill="both", expand=True, pady=(14, 0))
    overview.grid_columnconfigure(0, weight=1)
    overview.grid_columnconfigure(1, weight=1)

    answer_key_panel = tk.Frame(overview, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    answer_key_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
    student_summary_panel = tk.Frame(overview, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    student_summary_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
    result_summary_panel = tk.Frame(overview, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    result_summary_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(4, 0))

    update_answer_key_panel()
    update_student_and_result_panels()

    tip = tk.Frame(content, bg="#0B1423", highlightbackground=BORDER, highlightthickness=1)
    tip.pack(fill="x", pady=(12, 0), ipady=7)
    tk.Label(tip, text="i", font=("Segoe UI", 9, "bold"), fg="#3C8BFF", bg="#0B1423").pack(side="left", padx=(11, 8))
    tk.Label(tip, text="Tip: You can always perform these actions later from the project details page.", font=("Segoe UI", 8), fg=MUTED, bg="#0B1423").pack(side="left")

    return action_window


def _create_action_card(parent, row, column, icon, title, description, button_text, command=None):
    def trigger_action(event=None):
        if callable(command):
            command()

    card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
    card.grid(
        row=row,
        column=column,
        sticky="nsew",
        padx=(0, 7) if column == 0 else (7, 0),
        pady=(0, 8),
    )

    icon_label = tk.Label(card, text=icon, font=("Segoe UI", 22, "bold"), fg="#DCEAFF", bg="#173B78", width=2, height=1)
    title_label = tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL)
    desc_label = tk.Label(card, text=description, font=("Segoe UI", 8), fg=MUTED, bg=PANEL, justify="center")

    icon_label.pack(pady=(12, 7))
    title_label.pack()
    desc_label.pack(pady=(4, 10))

    button = tk.Button(
        card,
        text=button_text,
        command=trigger_action,
        font=("Segoe UI", 9, "bold"),
        fg="white",
        bg=BLUE,
        activebackground="#2B7CF0",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=13,
        pady=5,
        cursor="hand2",
    )
    button.pack(fill="x", padx=18, pady=(0, 12))

    for widget in (card, icon_label, title_label, desc_label):
        widget.bind("<Button-1>", trigger_action)
        widget.bind("<Enter>", lambda event, target=card: target.configure(highlightbackground="#3E7DF5"))
        widget.bind("<Leave>", lambda event, target=card: target.configure(highlightbackground=BORDER))