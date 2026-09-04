import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import requests

from scanner_integration import scan_answer_sheet_files
from storage import submit_submission


def choose_and_process_answer_sheets(parent, project, on_complete=None):
    files = filedialog.askopenfilenames(
        parent=parent.winfo_toplevel(),
        title="Upload Student Answer Sheets",
        filetypes=(("Answer sheets", "*.png *.jpg *.jpeg"), ("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg")),
    )
    if not files:
        return

    progress = tk.Toplevel(parent.winfo_toplevel())
    progress.title("Analyzing Answer Sheets")
    progress.configure(bg="#101722")
    progress.resizable(False, False)
    progress.transient(parent.winfo_toplevel())
    status = tk.StringVar(value=f"Analyzing {len(files)} answer sheet(s)...")
    tk.Label(progress, text="Analyzing Answer Sheets", font=("Segoe UI", 12, "bold"), fg="#F4F7FB", bg="#101722").pack(padx=28, pady=(22, 5))
    tk.Label(progress, textvariable=status, font=("Segoe UI", 9), fg="#AEB7C5", bg="#101722").pack(padx=28, pady=(0, 22))
    progress.grab_set()

    def worker():
        try:
            submissions, failures = scan_answer_sheet_files(files, project.get("question_count", 0))
            submitted = []
            for submission in submissions:
                try:
                    submitted.append(
                        submit_submission(
                            project["id"],
                            submission["sheet_id"],
                            submission["answers"],
                            submission.get("student"),
                            submission.get("scan"),
                            submission.get("student_details"),
                            submission.get("identity_status"),
                            submission.get("identity_mismatches"),
                        )
                    )
                except (KeyError, requests.RequestException) as error:
                    failures.append({"file": submission["file"], "error": str(error)})
            parent.after(0, finish, submitted, failures, None)
        except Exception as error:
            parent.after(0, finish, [], [], error)

    def finish(submitted, failures, error):
        progress.destroy()
        if error is not None:
            messagebox.showerror("Answer sheet analysis failed", str(error), parent=parent.winfo_toplevel())
            return
        if on_complete is not None:
            on_complete(submitted, failures)

    threading.Thread(target=worker, daemon=True).start()