import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import ImageTk
from functions import create_project_window
from storage import get_project, update_project
from theme import apply_theme


SERVICES_DIR = Path(__file__).resolve().parent.parent / "services"
if str(SERVICES_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SERVICES_DIR.parent))

from services.Generators import OMRGenerator


BG = "#080D17"
PANEL = "#101722"
BORDER = "#263242"
TEXT = "#F4F7FB"
MUTED = "#AEB7C5"
BLUE = "#1769E8"
INPUT = "#151E2B"


def create_omr_generator_page(parent, project=None, on_back=None, on_project_created=None, on_project_updated=None):
    page = tk.Frame(parent, bg=BG)
    preview_image = {"value": None}
    generated_pages = {"value": []}
    generated_generator = {"value": None}
    preview_job = {"value": None}
    project_sync_job = {"value": None}
    current_project = {"value": project}
    no_project_dialog = {"value": None}

    values = {
        "page_size": tk.StringVar(value="A4"),
        "orientation": tk.StringVar(value="Portrait"),
        "questions": tk.StringVar(value=str(project.get("question_count", "")) if project else ""),
        "options": tk.StringVar(value="4"),
        "name": tk.StringVar(value=""),
        "class_standard": tk.StringVar(value=""),
        "section": tk.StringVar(value=""),
        "admission": tk.StringVar(value=""),
        "title": tk.StringVar(value=project.get("name", "") if project else ""),
        "subject": tk.StringVar(value=""),
        "student_id": tk.StringVar(value=""),
        "qr_enabled": tk.BooleanVar(value=True),
    }
    student_choices = {}

    header = tk.Frame(page, bg=BG)
    header.pack(fill="x", padx=12, pady=(15, 9))
    tk.Button(header, text="Back", command=on_back, font=("Segoe UI", 9), fg="#4A99FF", bg=BG, activeforeground="#78B3FF", activebackground=BG, relief="flat", bd=0, cursor="hand2").pack(anchor="w")
    tk.Label(header, text="OMR Generator", font=("Segoe UI", 18, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(6, 0))
    project_label = tk.Label(header, text="", font=("Segoe UI", 9), fg=MUTED, bg=BG)
    project_label.pack(anchor="w")
    backend_status = tk.Label(header, text="", font=("Segoe UI", 8), fg=MUTED, bg=BG)
    backend_status.pack(anchor="w")

    body = tk.Frame(page, bg=BG)
    body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    settings = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, width=335)
    settings.pack(side="left", fill="y", padx=(0, 10))
    settings.pack_propagate(False)
    preview = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    preview.pack(side="left", fill="both", expand=True)
    preview.pack_propagate(False)

    tk.Label(settings, text="Generator Settings", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=12, pady=(10, 6))
    _select_row(settings, "Page Size", values["page_size"], ("A4", "A5", "A3", "Letter", "Legal"))
    _select_row(settings, "Orientation", values["orientation"], ("Portrait", "Landscape"))
    _entry_row(settings, "Number of Questions", values["questions"])
    _select_row(settings, "Options (Choices)", values["options"], ("2", "3", "4", "5", "6"))

    tk.Frame(settings, height=1, bg=BORDER).pack(fill="x", padx=12, pady=8)
    tk.Label(settings, text="Student Information", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=12, pady=(0, 5))
    student_grid = tk.Frame(settings, bg=PANEL)
    student_grid.pack(fill="x", padx=12)
    student_grid.grid_columnconfigure(0, weight=3)
    student_grid.grid_columnconfigure(1, weight=2)
    _entry_grid_row(student_grid, "Name", values["name"], 0, 0, column_span=2)
    _entry_grid_row(student_grid, "Class", values["class_standard"], 1, 0)
    _entry_grid_row(student_grid, "Section", values["section"], 1, 1)
    _entry_grid_row(student_grid, "Admission Number", values["admission"], 2, 0, column_span=2)
    _entry_grid_row(student_grid, "Subject", values["subject"], 3, 0, column_span=2)

    tk.Label(settings, text="Roster Student", font=("Segoe UI", 8), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(8, 1))
    student_selector = ttk.Combobox(settings, state="readonly", font=("Segoe UI", 9))
    student_selector.pack(fill="x", padx=12, ipady=3)

    tk.Label(settings, text="Answer Sheet Title", font=("Segoe UI", 8), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(8, 1))
    _entry_row(settings, "Project title", values["title"])

    action_block = tk.Frame(settings, bg=PANEL)
    action_block.pack(fill="x", padx=12, pady=(8, 2))

    generate_button = tk.Button(
        action_block,
        text="Generate OMR",
        command=lambda: generate_omr(),
        font=("Segoe UI", 9, "bold"),
        fg="white",
        bg=BLUE,
        activebackground="#2B7CF0",
        relief="flat",
        bd=0,
        pady=7,
        cursor="hand2",
    )
    generate_button.pack(fill="x", pady=(0, 8), ipady=2)

    tk.Checkbutton(
        action_block,
        text="Include QR code",
        variable=values["qr_enabled"],
        fg=MUTED,
        bg=PANEL,
        activebackground=PANEL,
        activeforeground=TEXT,
        selectcolor=INPUT,
        justify="left",
    ).pack(anchor="w")

    preview_header = tk.Label(preview, text="Live Preview", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL)
    preview_header.pack(anchor="w", padx=12, pady=(12, 4))
    image_container = tk.Frame(preview, bg=PANEL)
    image_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    image_label = tk.Label(image_container, text="Generate a preview to see the answer sheet.", font=("Segoe UI", 10), fg=MUTED, bg=PANEL)
    image_label.pack(fill="both", expand=True)

    def make_config():
        try:
            questions = max(1, int(values["questions"].get()))
        except ValueError:
            raise ValueError("Number of questions must be a positive integer.")
        options = max(2, min(6, int(values["options"].get())))
        return {
            "page_size": values["page_size"].get(),
            "orientation": values["orientation"].get(),
            "questions": questions,
            "choices": tuple("ABCDEF"[:options]),
            "name": values["name"].get(),
            "class_standard": values["class_standard"].get(),
            "class_division": values["section"].get(),
            "admission_number": values["admission"].get(),
            "title": values["title"].get(),
            "subject": values["subject"].get(),
            "student_id": values["student_id"].get(),
            "margin": 100,
            "header_height": 540,
            "start_y": 620,
            "bottom_margin": 180,
            "question_spacing": 105,
            "column_gap": 70,
            "bubble_spacing": 150,
            "bubble_radius": 24,
            "question_bubble_gap": 35,
            "qr_enabled": values["qr_enabled"].get(),
            "qr_position": "Top Right",
            "output_format": "PDF",
            "header_name": True,
            "header_class": True,
            "header_section": True,
            "header_admission": True,
            "header_subject": True,
        }

    def generate_preview():
        preview_job["value"] = None
        generated_generator["value"] = None
        if current_project["value"] is None:
            generated_pages["value"] = []
            image_label.configure(image="", text="Create a project to see the answer sheet preview.")
            image_label.image = None
            return

        preview_width = preview.winfo_width()
        preview_height = preview.winfo_height()
        if preview_width <= 50 or preview_height <= 50:
            page.after(100, generate_preview)
            return

        try:
            generator = OMRGenerator(make_config())
            generated_pages["value"] = generator.generate()
            generated_generator["value"] = generator
            page_image = generated_pages["value"][0].copy()
            page_image.thumbnail((max(1, image_label.winfo_width() - 20), max(1, image_label.winfo_height() - 20)))
            preview_image["value"] = ImageTk.PhotoImage(page_image)
            image_label.configure(image=preview_image["value"], text="")
            image_label.image = preview_image["value"]
            image_label.update_idletasks()
            image_label.bind("<Configure>", refresh_preview)
            page.after_idle(refresh_preview)
        except ValueError:
            return
        except Exception as error:
            generated_pages["value"] = []
            messagebox.showerror("Preview failed", f"Could not generate the OMR preview:\n\n{error}", parent=page.winfo_toplevel())

    def sync_project_values():
        project_sync_job["value"] = None
        selected_project = current_project["value"]
        if selected_project is None:
            return

        try:
            question_count = int(values["questions"].get())
            if question_count <= 0:
                return
        except ValueError:
            return

        project_name = values["title"].get().strip()
        if not project_name:
            return

        try:
            updated_project = update_project(selected_project["id"], project_name, question_count)
        except Exception as error:
            messagebox.showerror("Project update failed", f"Could not save project changes:\n\n{error}", parent=page.winfo_toplevel())
            if project_sync_job["value"] is not None:
                page.after_cancel(project_sync_job["value"])
                project_sync_job["value"] = None
            set_project(selected_project)
            return

        current_project["value"] = updated_project
        if on_project_updated is not None:
            on_project_updated(updated_project)

    def schedule_project_sync(*_):
        if project_sync_job["value"] is not None:
            page.after_cancel(project_sync_job["value"])
        project_sync_job["value"] = page.after(500, sync_project_values)

    def generate_omr():
        generate_preview()
        if generated_generator["value"] is not None:
            show_format_dialog()

    def show_format_dialog():
        owner = page.winfo_toplevel()
        dialog = tk.Toplevel(owner)
        dialog.title("Save OMR")
        dialog.configure(bg=PANEL)
        dialog.resizable(False, False)
        dialog.transient(owner)

        tk.Label(dialog, text="Choose OMR format", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL).pack(padx=22, pady=(16, 10))
        options = tk.Frame(dialog, bg=PANEL)
        options.pack(padx=14, pady=(0, 16))
        for output_format in ("PNG", "JPEG", "PDF"):
            tk.Button(
                options,
                text=output_format,
                command=lambda selected_format=output_format: export_omr(dialog, selected_format),
                font=("Segoe UI", 9, "bold"),
                fg=TEXT,
                bg=INPUT,
                activebackground="#202D3E",
                relief="flat",
                bd=0,
                padx=12,
                pady=5,
                cursor="hand2",
            ).pack(side="left", padx=4)

        apply_theme(dialog, getattr(owner, "_theme_mode", "dark"))
        owner.update_idletasks()
        dialog.update_idletasks()
        x_position = owner.winfo_rootx() + (owner.winfo_width() - dialog.winfo_width()) // 2
        y_position = owner.winfo_rooty() + (owner.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(0, x_position)}+{max(0, y_position)}")
        dialog.grab_set()

    def export_omr(dialog, output_format):
        dialog.destroy()
        generator = generated_generator["value"]
        if generator is None:
            return

        extension = output_format.lower()
        filename = filedialog.asksaveasfilename(
            parent=page.winfo_toplevel(),
            title=f"Save OMR as {output_format}",
            defaultextension=f".{extension}",
            filetypes=((f"{output_format} files", f"*.{extension}"),),
        )
        if not filename:
            return

        try:
            if output_format == "PDF":
                generator.save_pdf(filename)
            elif output_format == "JPEG":
                generator.save_jpeg(str(Path(filename).with_suffix("")), extension=".jpeg")
            else:
                generator.save_png(str(Path(filename).with_suffix("")))
            messagebox.showinfo("OMR saved", f"The OMR {output_format} was saved successfully.", parent=page.winfo_toplevel())
        except Exception as error:
            messagebox.showerror("Export failed", f"Could not save the OMR:\n\n{error}", parent=page.winfo_toplevel())

    def refresh_preview():
        pages = generated_pages["value"]
        if not pages or image_label.winfo_width() <= 1:
            return
        page_image = pages[0].copy()
        page_image.thumbnail((max(1, image_label.winfo_width() - 20), max(1, image_label.winfo_height() - 20)))
        preview_image["value"] = ImageTk.PhotoImage(page_image)
        image_label.configure(image=preview_image["value"])
        image_label.image = preview_image["value"]

    def show_no_project_dialog():
        if current_project["value"] is not None or no_project_dialog["value"] is not None:
            return

        owner = page.winfo_toplevel()
        owner.update_idletasks()
        dialog = tk.Toplevel(owner)
        no_project_dialog["value"] = dialog
        dialog.title("No project yet")
        dialog.configure(bg=PANEL)
        dialog.resizable(False, False)
        dialog.transient(owner)

        tk.Label(
            dialog,
            text="No project yet",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT,
            bg=PANEL,
        ).pack(padx=30, pady=(22, 5))
        tk.Label(
            dialog,
            text="Create a new project to show the live preview.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL,
        ).pack(padx=30, pady=(0, 16))

        def create_project():
            dialog.destroy()
            no_project_dialog["value"] = None

            def handle_created(created_project):
                set_project(created_project)
                if on_project_created is not None:
                    on_project_created(created_project)

            project_dialog = create_project_window(page.winfo_toplevel(), handle_created)
            apply_theme(project_dialog, getattr(owner, "_theme_mode", "dark"))

        tk.Button(
            dialog,
            text="Create Project",
            command=create_project,
            font=("Segoe UI", 9, "bold"),
            fg="white",
            bg=BLUE,
            activebackground="#2B7CF0",
            relief="flat",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
        ).pack(pady=(0, 20))

        apply_theme(dialog, getattr(owner, "_theme_mode", "dark"))
        dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), no_project_dialog.update(value=None)))
        dialog.grab_set()
        dialog.update_idletasks()
        x_position = owner.winfo_rootx() + (owner.winfo_width() - dialog.winfo_width()) // 2
        y_position = owner.winfo_rooty() + (owner.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(0, x_position)}+{max(0, y_position)}")

    def schedule_preview(*_):
        if preview_job["value"] is not None:
            page.after_cancel(preview_job["value"])
        preview_job["value"] = page.after(250, generate_preview)

    def set_project(next_project):
        selected_project = next_project
        if selected_project is None:
            current_project["value"] = None
            project_label.configure(text="No project selected")
            backend_status.configure(text="Create a project to begin generating OMR sheets.")
            values["questions"].set("")
            values["title"].set("")
            values["subject"].set("")
            values["student_id"].set("")
            student_choices.clear()
            student_selector["values"] = ()
            student_selector.set("")
            generated_pages["value"] = []
            generated_generator["value"] = None
            image_label.configure(image="", text="Create a project to see the answer sheet preview.")
            image_label.image = None
            return

        if selected_project.get("id"):
            try:
                selected_project = get_project(selected_project["id"])
            except Exception as error:
                messagebox.showerror("Project unavailable", f"Could not retrieve project data:\n\n{error}", parent=page.winfo_toplevel())
                return
        current_project["value"] = selected_project
        project_label.configure(
            text=f"Project: {current_project['value'].get('name', 'Untitled Project')}  -  {current_project['value'].get('question_count', 0)} Questions"
        )
        backend_status.configure(
            text=(
                f"Backend ID: {current_project['value'].get('id', 'local preview')}  |  "
                f"Answer key: {'ready' if current_project['value'].get('answer_key') else 'not set'}  |  "
                f"Students: {len(current_project['value'].get('students') or [])}  |  "
                f"Results: {len(current_project['value'].get('results') or [])}"
            )
        )
        values["questions"].set(str(current_project["value"].get("question_count", "")))
        values["title"].set(current_project["value"].get("name", ""))
        student_choices.clear()
        student_labels = []
        for student in current_project["value"].get("students") or []:
            label = f"{student.get('name', 'Unnamed student')} ({student.get('roll_no', 'No roll number')})"
            student_choices[label] = student
            student_labels.append(label)
        student_selector["values"] = student_labels
        student_selector.set("")
        schedule_preview()

    def select_roster_student(event=None):
        student = student_choices.get(student_selector.get())
        if student is None:
            values["student_id"].set("")
            return
        values["student_id"].set(str(student.get("sheet_id") or student.get("id", "")).strip())
        values["name"].set(student.get("name", ""))
        values["class_standard"].set(student.get("class", ""))
        values["section"].set(student.get("section", ""))
        values["admission"].set(student.get("roll_no", ""))

    student_selector.bind("<<ComboboxSelected>>", select_roster_student)

    page.set_project = set_project
    page.show_no_project_dialog = show_no_project_dialog
    set_project(project)

    for variable in values.values():
        variable.trace_add("write", schedule_preview)
    values["questions"].trace_add("write", schedule_project_sync)
    values["title"].trace_add("write", schedule_project_sync)

    if project is not None:
        page.after(100, generate_preview)
    return page


def _entry_row(parent, label, variable):
    tk.Label(parent, text=label, font=("Segoe UI", 8), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(1, 1))
    tk.Entry(parent, textvariable=variable, font=("Segoe UI", 9), fg=TEXT, bg=INPUT, insertbackground=TEXT, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=BLUE).pack(fill="x", padx=12, ipady=5)


def _entry_grid_row(parent, label, variable, row, column, column_span=1):
    tk.Label(parent, text=label, font=("Segoe UI", 8), fg=MUTED, bg=PANEL).grid(row=row * 2, column=column, columnspan=column_span, sticky="w", padx=(0, 8) if column == 0 and column_span == 1 else 0, pady=(1, 1))
    entry = tk.Entry(parent, textvariable=variable, font=("Segoe UI", 9), fg=TEXT, bg=INPUT, insertbackground=TEXT, relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=BLUE)
    entry.grid(row=row * 2 + 1, column=column, columnspan=column_span, sticky="ew", padx=(0, 8) if column == 0 and column_span == 1 else 0, pady=(0, 5), ipady=4)


def _select_row(parent, label, variable, options):
    tk.Label(parent, text=label, font=("Segoe UI", 8), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(1, 1))
    option_menu = tk.OptionMenu(parent, variable, *options)
    option_menu.configure(fg=TEXT, bg=INPUT, activeforeground=TEXT, activebackground="#202D3E", highlightbackground=BORDER, highlightthickness=1, relief="flat")
    option_menu.pack(fill="x", padx=12, pady=(0, 2))
    option_menu["menu"].configure(bg=INPUT, fg=TEXT, activebackground=BLUE, activeforeground=TEXT)