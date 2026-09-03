import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import requests

from assets import asset_path
from project_action import parse_answer_key_csv
from storage import get_project, load_results, update_answer_key
from answer_key import answer_key_menu, open_answer_key_editor
from answer_sheet_workflow import choose_and_process_answer_sheets
from analysis_window import open_analysis_window

BG = "#080D17"
PANEL = "#101722"
BORDER = "#263242"
TEXT = "#F4F7FB"
MUTED = "#AEB7C5"
BLUE = "#1769E8"
INPUT = "#151E2B"


def create_project_details_page(parent, project, on_back=None, on_generate_omr=None, on_project_updated=None):
    page = tk.Frame(parent, bg=BG)
    page.pack_propagate(False)
    page.project = project or {}

    def refresh_project_data():
        try:
            page.project = get_project(page.project.get("id"))
        except (KeyError, requests.RequestException):
            return
        if on_project_updated is not None:
            on_project_updated(page.project)
        render()

    def render():
        for child in page.winfo_children():
            child.destroy()

        header = tk.Frame(page, bg=BG)
        header.pack(fill="x", padx=18, pady=(16, 12))
        tk.Button(
            header,
            text="Back",
            command=on_back if on_back is not None else lambda: None,
            font=("Segoe UI", 9),
            fg="#4A99FF",
            bg=BG,
            activeforeground="#78B3FF",
            activebackground=BG,
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(anchor="w")

        title = page.project.get("name", "Untitled Project")
        tk.Label(header, text=title, font=("Segoe UI", 22, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(8, 0))
        tk.Label(header, text=f"{page.project.get('question_count', 0)} questions • {len(page.project.get('students') or [])} students • {len(page.project.get('results') or [])} results", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(anchor="w")

        actions = tk.Frame(page, bg=BG)
        actions.pack(fill="x", padx=18, pady=(0, 12))

        def upload_answer_key():
            filename = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv"),))
            if not filename:
                return
            try:
                with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                    answers = parse_answer_key_csv(list(csv.reader(file)), page.project.get("question_count", 0))
                update_answer_key(page.project["id"], answers)
                refresh_project_data()
                messagebox.showinfo("Answer key uploaded", "The answer key was saved successfully.")
            except (OSError, ValueError, KeyError, requests.RequestException) as error:
                messagebox.showerror("Answer key upload failed", str(error))

        def create_answer_key():
            open_answer_key_editor(page, page.project, refresh_project_data)

        def upload_answer_sheets():
            def completed(submitted, failures):
                refresh_project_data()
                open_analysis_window(page, page.project, submitted, failures)

            choose_and_process_answer_sheets(page, page.project, completed)

        def show_answer_key_menu(button):
            menu = answer_key_menu(button, page.project, refresh_project_data)
            menu.post(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())

        def open_saved_analysis():
            try:
                open_analysis_window(page, page.project, load_results(page.project["id"]))
            except (KeyError, requests.RequestException) as error:
                messagebox.showerror("Analysis unavailable", str(error))

        button_kwargs = {
            "font": ("Segoe UI", 9, "bold"),
            "fg": "white",
            "bg": BLUE,
            "activebackground": "#2B7CF0",
            "activeforeground": "white",
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "padx": 12,
            "pady": 7,
        }

        tk.Button(actions, text="Generate OMR", command=lambda: on_generate_omr(page.project) if on_generate_omr else None, **button_kwargs).pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Upload Answer Sheets", command=upload_answer_sheets, **button_kwargs).pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Create Answer Key", command=create_answer_key, **button_kwargs).pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Upload Answer Key", command=upload_answer_key, **button_kwargs).pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Analyze Results", command=open_saved_analysis, **button_kwargs).pack(side="left")
        if page.project.get("answer_key"):
            menu_button = tk.Button(actions, text="...", font=("Segoe UI", 10, "bold"), fg="white", bg=BLUE, activebackground="#2B7CF0", relief="flat", bd=0, padx=12, pady=6)
            menu_button.pack(side="left")
            menu_button.configure(command=lambda: answer_key_menu(menu_button, page.project, refresh_project_data).post(menu_button.winfo_rootx(), menu_button.winfo_rooty() + menu_button.winfo_height()))

        stats = tk.Frame(page, bg=BG)
        stats.pack(fill="x", padx=18, pady=(0, 12))
        stats.grid_columnconfigure(0, weight=1)
        stats.grid_columnconfigure(1, weight=1)
        stats.grid_columnconfigure(2, weight=1)
        stats.grid_columnconfigure(3, weight=1)

        summary_cards = [
            ("Students", str(len(page.project.get("students") or []))),
            ("Answer Key", "Ready" if page.project.get("answer_key") else "Missing"),
            ("Results", str(len(page.project.get("results") or []))),
            ("Questions", str(page.project.get("question_count", 0))),
        ]

        for index, (label, value) in enumerate(summary_cards):
            card = tk.Frame(stats, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 8) if index < 3 else 0)
            tk.Label(card, text=label, font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(10, 2))
            tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=12, pady=(0, 12))

        result_table = tk.Frame(page, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        result_table.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        table_label = tk.Label(result_table, text="Results", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL)
        table_label.pack(anchor="w", padx=12, pady=(10, 6))

        columns = ("sheet_id", "student", "correct", "incorrect", "unattempted", "marks")
        tree = ttk.Treeview(result_table, columns=columns, show="headings", height=12)
        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        headings = {
            "sheet_id": "Sheet ID",
            "student": "Student",
            "correct": "Correct",
            "incorrect": "Incorrect",
            "unattempted": "Unattempted",
            "marks": "Marks",
        }
        for key, label in headings.items():
            tree.heading(key, text=label)
            tree.column(key, width=130, anchor="center")

        for result in page.project.get("results") or []:
            tree.insert(
                "",
                "end",
                values=(
                    result.get("sheet_id", "-"),
                    result.get("student_name", "-"),
                    result.get("correct", 0),
                    result.get("incorrect", 0),
                    result.get("unattempted", 0),
                    result.get("marks", 0),
                ),
            )

        if not (page.project.get("results") or []):
            tk.Label(result_table, text="No results yet. Scan and submit an answer sheet to populate this table.", font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(0, 14))

    render()
    return page
