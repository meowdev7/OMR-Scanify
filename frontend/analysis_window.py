import tkinter as tk
from tkinter import ttk

from theme import PALETTES, apply_theme, resolve_theme


BG = "#080D17"
PANEL = "#101722"
BORDER = "#263242"
TEXT = "#F4F7FB"
MUTED = "#AEB7C5"
BLUE = "#1769E8"


def open_analysis_window(parent, project, results=None, failures=None):
    palette = PALETTES[resolve_theme(getattr(parent.winfo_toplevel(), "_theme_mode", "dark"))]
    window = tk.Toplevel(parent.winfo_toplevel())
    window.title(f"Analysis - {project.get('name', 'Project')}")
    window.geometry("980x680")
    window.minsize(760, 520)
    window.configure(bg=palette["window"])
    window.transient(parent.winfo_toplevel())

    results = list(results or [])
    failures = list(failures or [])

    header = tk.Frame(window, bg=palette["window"])
    header.pack(fill="x", padx=22, pady=(18, 10))
    tk.Label(header, text="Analysis", font=("Segoe UI", 18, "bold"), fg=palette["text"], bg=palette["window"]).pack(anchor="w")
    tk.Label(header, text=project.get("name", "Untitled Project"), font=("Segoe UI", 9), fg=palette["muted"], bg=palette["window"]).pack(anchor="w", pady=(3, 0))

    summary = tk.Frame(window, bg=palette["window"])
    summary.pack(fill="x", padx=22, pady=(0, 12))
    summary_metrics = (
        ("Analyzed", str(len(results))),
        ("Failed", str(len(failures))),
        ("Questions", str(project.get("question_count", 0))),
    )
    if results:
        first_result = results[0]
        summary_metrics += (
            ("Score", f"{first_result.get('marks', 0)}/{first_result.get('total_questions', 0)}"),
            ("Correct", str(first_result.get("correct", 0))),
            ("Incorrect", str(first_result.get("incorrect", 0))),
            ("Unattempted", str(first_result.get("unattempted", 0))),
        )
    for index, (label, value) in enumerate(summary_metrics):
        _summary_value(summary, label, value, index % 4, index // 4, palette)
    for column in range(4):
        summary.grid_columnconfigure(column, weight=1)

    if failures:
        failure_panel = tk.Frame(window, bg=palette["panel_alt"], highlightbackground=palette["border"], highlightthickness=1)
        failure_panel.pack(fill="x", padx=22, pady=(0, 12))
        tk.Label(failure_panel, text="Files that need attention", font=("Segoe UI", 10, "bold"), fg=palette["text"], bg=palette["panel_alt"]).pack(anchor="w", padx=12, pady=(8, 4))
        for failure in failures:
            tk.Label(failure_panel, text=f"{failure.get('file', 'Unknown file')}: {failure.get('error', 'Unknown error')}", font=("Segoe UI", 8), fg=palette["muted"], bg=palette["panel_alt"], anchor="w", justify="left", wraplength=900).pack(fill="x", padx=12, pady=(0, 5))

    body = tk.Frame(window, bg=palette["window"])
    body.pack(fill="both", expand=True, padx=22, pady=(0, 18))
    body.grid_columnconfigure(0, weight=1, minsize=230)
    body.grid_columnconfigure(1, weight=3)
    body.grid_rowconfigure(0, weight=1)

    sheet_panel = tk.Frame(body, bg=palette["panel"], highlightbackground=palette["border"], highlightthickness=1)
    sheet_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    tk.Label(sheet_panel, text="Sheets", font=("Segoe UI", 10, "bold"), fg=palette["text"], bg=palette["panel"]).pack(anchor="w", padx=12, pady=(12, 8))
    sheet_list = tk.Listbox(sheet_panel, exportselection=False, bg=palette["panel_alt"], fg=palette["text"], selectbackground=palette["blue"], selectforeground=palette["text"], relief="flat", highlightthickness=0, font=("Segoe UI", 9))
    sheet_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    detail_panel = tk.Frame(body, bg=palette["panel"], highlightbackground=palette["border"], highlightthickness=1)
    detail_panel.grid(row=0, column=1, sticky="nsew")
    detail_panel.grid_rowconfigure(2, weight=1)
    detail_panel.grid_columnconfigure(0, weight=1)

    identity = tk.Label(detail_panel, text="Select a sheet to inspect its analysis.", font=("Segoe UI", 11, "bold"), fg=palette["text"], bg=palette["panel"], anchor="w", justify="left")
    identity.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 3))
    score = tk.Label(detail_panel, text="", font=("Segoe UI", 9), fg=palette["muted"], bg=palette["panel"], anchor="w")
    score.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

    columns = ("question", "correct", "scanned", "status", "confidence", "page")
    table = ttk.Treeview(detail_panel, columns=columns, show="headings")
    scrollbar = ttk.Scrollbar(detail_panel, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    table.grid(row=2, column=0, sticky="nsew", padx=(12, 0), pady=(0, 12))
    scrollbar.grid(row=2, column=1, sticky="ns", padx=(0, 12), pady=(0, 12))
    headings = {"question": "Question", "correct": "Key", "scanned": "Scanned", "status": "Status", "confidence": "Confidence", "page": "Page"}
    widths = {"question": 72, "correct": 72, "scanned": 78, "status": 100, "confidence": 92, "page": 58}
    for column in columns:
        table.heading(column, text=headings[column])
        table.column(column, width=widths[column], anchor="center")

    def show_result(index):
        if not results or index < 0 or index >= len(results):
            identity.configure(text="No analyzed sheets")
            score.configure(text="Upload a sheet with a readable QR code and matching answer key.")
            table.delete(*table.get_children())
            return
        result = results[index]
        identity.configure(text=f"{result.get('student_name', 'Unknown student')}  |  {result.get('sheet_id', '-')}")
        score.configure(text=f"Score: {result.get('marks', 0)}/{result.get('total_questions', 0)}    Correct {result.get('correct', 0)}    Incorrect {result.get('incorrect', 0)}    Unattempted {result.get('unattempted', 0)}")
        table.delete(*table.get_children())
        for question in result.get("questions") or []:
            scanned = question.get("scanned_answer") or "-"
            confidence = question.get("confidence", 0)
            confidence_text = f"{confidence:.0%}" if isinstance(confidence, (int, float)) else str(confidence)
            table.insert("", "end", values=(question.get("question", "-"), question.get("correct_answer", "-"), scanned, question.get("status", "-"), confidence_text, question.get("page", "-")))

    for result in results:
        sheet_list.insert("end", f"{result.get('student_name', 'Unknown student')}  |  {result.get('sheet_id', '-')}")
    sheet_list.bind("<<ListboxSelect>>", lambda event: show_result(sheet_list.curselection()[0]) if sheet_list.curselection() else None)
    if results:
        sheet_list.selection_set(0)
        show_result(0)
    else:
        show_result(-1)

    apply_theme(window, getattr(parent.winfo_toplevel(), "_theme_mode", "dark"))
    window.grab_set()
    return window


def _summary_value(parent, label, value, column, row, palette):
    card = tk.Frame(parent, bg=palette["panel"], highlightbackground=palette["border"], highlightthickness=1)
    card.grid(row=row, column=column, sticky="ew", padx=(0, 8) if column < 3 else 0, pady=(0, 8) if row == 0 else 0)
    tk.Label(card, text=label, font=("Segoe UI", 8), fg=palette["muted"], bg=palette["panel"]).pack(anchor="w", padx=12, pady=(8, 1))
    tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), fg=palette["text"], bg=palette["panel"]).pack(anchor="w", padx=12, pady=(0, 8))
