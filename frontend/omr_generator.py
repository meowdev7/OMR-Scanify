import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import ImageTk


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


def create_omr_generator_page(parent, project=None, on_back=None):
    project = project or {"name": "Physics Test", "question_count": 50}
    page = tk.Frame(parent, bg=BG)
    preview_image = {"value": None}
    generated_pages = {"value": []}

    values = {
        "page_size": tk.StringVar(value="A4"),
        "orientation": tk.StringVar(value="Portrait"),
        "questions": tk.StringVar(value=str(project.get("question_count", 50))),
        "options": tk.StringVar(value="4"),
        "name": tk.StringVar(value="John Doe"),
        "class_standard": tk.StringVar(value="XII"),
        "section": tk.StringVar(value="A"),
        "admission": tk.StringVar(value="12345"),
        "subject": tk.StringVar(value=project.get("name", "Physics")),
        "qr_enabled": tk.BooleanVar(value=True),
    }

    header = tk.Frame(page, bg=BG)
    header.pack(fill="x", padx=12, pady=(15, 9))
    tk.Button(header, text="<-  Back to Project Actions", command=on_back, font=("Segoe UI", 9), fg="#4A99FF", bg=BG, activeforeground="#78B3FF", activebackground=BG, relief="flat", bd=0, cursor="hand2").pack(anchor="w")
    tk.Label(header, text="OMR Generator", font=("Segoe UI", 18, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(8, 0))
    tk.Label(header, text=f"Project: {project.get('name', 'Untitled Project')}  -  {project.get('question_count', 0)} Questions", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(anchor="w")

    body = tk.Frame(page, bg=BG)
    body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    settings = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, width=315)
    settings.pack(side="left", fill="y", padx=(0, 10))
    settings.pack_propagate(False)
    preview = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    preview.pack(side="left", fill="both", expand=True)

    tk.Label(settings, text="Generator Settings", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=12, pady=(12, 10))
    _select_row(settings, "Page Size", values["page_size"], ("A4", "A5", "A3", "Letter", "Legal"))
    _select_row(settings, "Orientation", values["orientation"], ("Portrait", "Landscape"))
    _entry_row(settings, "Number of Questions", values["questions"])
    _select_row(settings, "Options (Choices)", values["options"], ("2", "3", "4", "5", "6"))

    tk.Frame(settings, height=1, bg=BORDER).pack(fill="x", padx=12, pady=12)
    tk.Label(settings, text="Student Information", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=12, pady=(0, 8))
    _entry_row(settings, "Name", values["name"])
    _entry_row(settings, "Class", values["class_standard"])
    _entry_row(settings, "Section", values["section"])
    _entry_row(settings, "Admission Number", values["admission"])
    _entry_row(settings, "Subject", values["subject"])
    tk.Checkbutton(settings, text="Include QR code", variable=values["qr_enabled"], fg=MUTED, bg=PANEL, activebackground=PANEL, activeforeground=TEXT, selectcolor=INPUT).pack(anchor="w", padx=9, pady=(7, 5))

    generate_button = tk.Button(settings, text="↻  Generate / Update Preview", command=lambda: generate_preview(), font=("Segoe UI", 9, "bold"), fg="white", bg=BLUE, activebackground="#2B7CF0", relief="flat", bd=0, pady=7, cursor="hand2")
    generate_button.pack(fill="x", padx=12, pady=(8, 8))
    tk.Button(settings, text="↓  Save OMR as PDF", command=lambda: save_pdf(), font=("Segoe UI", 9), fg=TEXT, bg=INPUT, activebackground="#202D3E", relief="flat", bd=0, pady=7, cursor="hand2").pack(fill="x", padx=12)

    tk.Label(preview, text="Live Preview", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=PANEL).pack(anchor="w", padx=12, pady=(12, 4))
    image_label = tk.Label(preview, text="Generate a preview to see the answer sheet.", font=("Segoe UI", 10), fg=MUTED, bg=PANEL)
    image_label.pack(fill="both", expand=True, padx=12, pady=12)

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
            "subject": values["subject"].get(),
            "margin": 100,
            "header_height": 470,
            "start_y": 560,
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
        preview_width = preview.winfo_width()
        preview_height = preview.winfo_height()
        if preview_width <= 50 or preview_height <= 50:
            page.after(100, generate_preview)
            return

        try:
            generator = OMRGenerator(make_config())
            generated_pages["value"] = generator.generate()
            page_image = generated_pages["value"][0].copy()
            page_image.thumbnail((max(1, preview_width - 35), max(1, preview_height - 55)))
            preview_image["value"] = ImageTk.PhotoImage(page_image)
            image_label.configure(image=preview_image["value"], text="")
            image_label.image = preview_image["value"]
            image_label.update_idletasks()
            image_label.bind("<Configure>", refresh_preview)
        except Exception as error:
            generated_pages["value"] = []
            messagebox.showerror("Preview failed", f"Could not generate the OMR preview:\n\n{error}", parent=page.winfo_toplevel())

    def refresh_preview():
        pages = generated_pages["value"]
        if not pages or image_label.winfo_width() <= 1:
            return
        page_image = pages[0].copy()
        page_image.thumbnail((max(1, image_label.winfo_width() - 20), max(1, image_label.winfo_height() - 20)))
        preview_image["value"] = ImageTk.PhotoImage(page_image)
        image_label.configure(image=preview_image["value"])
        image_label.image = preview_image["value"]

    def save_pdf():
        if not generated_pages["value"]:
            generate_preview()
        if not generated_pages["value"]:
            return
        filename = filedialog.asksaveasfilename(parent=page.winfo_toplevel(), defaultextension=".pdf", filetypes=(("PDF files", "*.pdf"),))
        if filename:
            generator = OMRGenerator(make_config())
            generator.generate()
            generator.save_pdf(filename)
            messagebox.showinfo("OMR saved", "The OMR PDF was saved successfully.", parent=page.winfo_toplevel())

    page.after(100, generate_preview)
    return page


def _entry_row(parent, label, variable):
    tk.Label(parent, text=label, font=("Segoe UI", 8), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(3, 2))
    tk.Entry(parent, textvariable=variable, font=("Segoe UI", 9), fg=TEXT, bg=INPUT, insertbackground=TEXT, relief="flat", bd=0).pack(fill="x", padx=12, ipady=5)


def _select_row(parent, label, variable, options):
    tk.Label(parent, text=label, font=("Segoe UI", 8), fg=MUTED, bg=PANEL).pack(anchor="w", padx=12, pady=(3, 2))
    tk.OptionMenu(parent, variable, *options).pack(fill="x", padx=12, pady=(0, 3))