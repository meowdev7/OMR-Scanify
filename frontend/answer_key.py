import csv
import tkinter as tk
from tkinter import filedialog, messagebox

import requests
from PIL import Image, ImageDraw, ImageFont

from storage import delete_answer_key, update_answer_key


BG = "#080D17"
PANEL = "#101722"
BORDER = "#263242"
TEXT = "#F4F7FB"
MUTED = "#AEB7C5"
BLUE = "#1769E8"
CHOICES = ("A", "B", "C", "D")


def open_answer_key_editor(parent, project, on_saved=None):
    question_count = int(project.get("question_count", 0))
    answers = list(project.get("answer_key") or [])
    if len(answers) != question_count:
        answers = [""] * question_count

    dialog = tk.Toplevel(parent.winfo_toplevel())
    dialog.title(f"Answer Key - {project.get('name', 'Project')}")
    dialog.configure(bg=BG)
    dialog.geometry("720x680")
    dialog.minsize(560, 420)
    dialog.transient(parent.winfo_toplevel())
    dialog.grab_set()

    tk.Label(dialog, text="Create Answer Key", font=("Segoe UI", 18, "bold"), fg=TEXT, bg=BG).pack(anchor="w", padx=24, pady=(20, 2))
    tk.Label(dialog, text=f"Select one correct option for each of the {question_count} questions.", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(anchor="w", padx=24, pady=(0, 14))

    canvas = tk.Canvas(dialog, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas, bg=BG)
    canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(24, 0), pady=(0, 14))
    scrollbar.pack(side="right", fill="y", padx=(0, 24), pady=(0, 14))
    content.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    editor_bind_tag = "AnswerKeyEditor"

    def scroll_questions(event):
        event_number = getattr(event, "num", None)
        if event_number == 4:
            canvas.yview_scroll(-3, "units")
        elif event_number == 5:
            canvas.yview_scroll(3, "units")
        else:
            canvas.yview_scroll(-int(event.delta / 120), "units")
        return "break"

    dialog.bind_class(editor_bind_tag, "<MouseWheel>", scroll_questions)
    dialog.bind_class(editor_bind_tag, "<Button-4>", scroll_questions)
    dialog.bind_class(editor_bind_tag, "<Button-5>", scroll_questions)

    def add_editor_bind_tag(widget):
        widget.bindtags((editor_bind_tag,) + widget.bindtags())
        for child in widget.winfo_children():
            add_editor_bind_tag(child)

    variables = []
    for index in range(question_count):
        row = tk.Frame(content, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=(0, 6))
        tk.Label(row, text=f"Question {index + 1}", width=15, anchor="w", font=("Segoe UI", 9, "bold"), fg=TEXT, bg=PANEL).pack(side="left", padx=(14, 8), pady=9)
        variable = tk.StringVar(value=answers[index])
        variables.append(variable)
        for choice in CHOICES:
            tk.Radiobutton(row, text=choice, value=choice, variable=variable, indicatoron=False, width=4, font=("Segoe UI", 9, "bold"), fg=TEXT, bg="#172338", selectcolor=BLUE, activebackground="#234A86", activeforeground=TEXT, relief="flat", bd=0).pack(side="left", padx=3, pady=6)

    add_editor_bind_tag(content)

    def save():
        selected = [variable.get() for variable in variables]
        missing = next((index + 1 for index, value in enumerate(selected) if not value), None)
        if missing is not None:
            messagebox.showerror("Answer key incomplete", f"Select an answer for question {missing}.", parent=dialog)
            return
        try:
            update_answer_key(project["id"], selected)
            if on_saved:
                on_saved()
            dialog.destroy()
        except (KeyError, requests.RequestException) as error:
            messagebox.showerror("Answer key save failed", str(error), parent=dialog)

    def reset_answers():
        if not messagebox.askyesno("Reset answer key", "Clear all selected answers?", parent=dialog):
            return
        for variable in variables:
            variable.set("")

    footer = tk.Frame(dialog, bg=BG)
    footer.pack(fill="x", padx=24, pady=(0, 20))
    tk.Button(footer, text="Cancel", command=dialog.destroy, font=("Segoe UI", 9), fg=MUTED, bg=BG, activebackground=BG, activeforeground=TEXT, relief="flat", bd=0, padx=12, pady=7).pack(side="right", padx=(8, 0))
    tk.Button(footer, text="Save Answer Key", command=save, font=("Segoe UI", 9, "bold"), fg="white", bg=BLUE, activebackground="#2B7CF0", relief="flat", bd=0, padx=14, pady=7).pack(side="right")
    tk.Button(footer, text="Reset", command=reset_answers, font=("Segoe UI", 9), fg="#FFB4B4", bg=BG, activebackground=BG, activeforeground="#FFD1D1", relief="flat", bd=0, padx=12, pady=7).pack(side="left")


def answer_key_menu(parent, project, on_changed=None):
    menu = tk.Menu(parent, tearoff=False)

    def changed():
        if on_changed:
            on_changed()

    menu.add_command(label="Change answer key", command=lambda: open_answer_key_editor(parent, project, changed))
    menu.add_command(label="Save as PNG", command=lambda: export_answer_key(parent, project, "png"))
    menu.add_command(label="Save as JPEG", command=lambda: export_answer_key(parent, project, "jpeg"))
    menu.add_command(label="Save as CSV", command=lambda: export_answer_key(parent, project, "csv"))
    menu.add_separator()

    def remove():
        if not messagebox.askyesno("Delete answer key", "Delete this answer key?", parent=parent.winfo_toplevel()):
            return
        try:
            delete_answer_key(project["id"])
            changed()
        except (KeyError, requests.RequestException) as error:
            messagebox.showerror("Delete failed", str(error), parent=parent.winfo_toplevel())

    menu.add_command(label="Delete answer key", command=remove)
    return menu


def export_answer_key(parent, project, file_format):
    answers = project.get("answer_key") or []
    if not answers:
        messagebox.showinfo("Answer key unavailable", "Save an answer key before exporting it.", parent=parent.winfo_toplevel())
        return
    extension = "jpg" if file_format == "jpeg" else file_format
    filename = filedialog.asksaveasfilename(parent=parent.winfo_toplevel(), defaultextension=f".{extension}", initialfile=f"{project.get('name', 'project')}_answer_key.{extension}", filetypes=((f"{file_format.upper()} files", f"*.{extension}"),))
    if not filename:
        return
    try:
        if file_format == "csv":
            with open(filename, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(("question", "answer"))
                writer.writerows((index, answer) for index, answer in enumerate(answers, start=1))
        else:
            image = _answer_key_image(project, answers)
            image.save(filename, format="JPEG" if file_format == "jpeg" else "PNG")
        messagebox.showinfo("Answer key exported", f"The answer key was saved to:\n{filename}", parent=parent.winfo_toplevel())
    except (OSError, ValueError) as error:
        messagebox.showerror("Export failed", str(error), parent=parent.winfo_toplevel())


def _answer_key_image(project, answers):
    image = Image.new("RGB", (1200, max(180, 100 + len(answers) * 42)), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((50, 35), f"{project.get('name', 'Project')} - Answer Key", fill="#111111", font=font)
    for index, answer in enumerate(answers, start=1):
        y = 90 + (index - 1) * 42
        draw.text((60, y), f"Question {index}", fill="#111111", font=font)
        for choice_index, choice in enumerate(CHOICES):
            x = 310 + choice_index * 150
            draw.ellipse((x, y - 4, x + 24, y + 20), outline="#111111", width=2)
            if choice == answer:
                draw.ellipse((x + 6, y + 2, x + 18, y + 14), fill="#1769E8")
            draw.text((x + 34, y), choice, fill="#111111", font=font)
    return image