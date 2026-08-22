# # # import PySimpleGUI as sg
# # # import os
# # #
# # #
# # # class CustomText(sg.Text):
# # #     """A custom text element with predefined styling."""
# # #
# # #     def __init__(self, text, *args, **kwargs):
# # #         # Define default styles
# # #         default_font = ('Helvetica', 12, 'bold')
# # #         default_color = '#FFFFFF'
# # #         default_bg = '#4A90E2'
# # #
# # #         # Merge user kwargs with defaults
# # #         kwargs['font'] = kwargs.get('font', default_font)
# # #         kwargs['text_color'] = kwargs.get('text_color', default_color)
# # #         kwargs['background_color'] = kwargs.get('background_color', default_bg)
# # #
# # #         # Initialize the parent PySimpleGUI Text class
# # #         super().__init__(text, *args, **kwargs)
# # #
# # #
# # # def OMR_generation_form():
# # #     bg_color = "#212121"
# # #     button_color = "#2b2a33"
# # #     buffer = 20
# # #     questions = 0
# # #     layout = [
# # #         [sg.Text("", size=(70, 2), justification="center", background_color=bg_color)],
# # #
# # #         [sg.Text("Name: ", size=(buffer, 2), background_color=bg_color), sg.Input(key="Name")],
# # #         [sg.Text("Class: ", size=(buffer, 2), background_color=bg_color), sg.Input(size=(10, 1), key="Class")],
# # #         [sg.Text("Section", size=(buffer, 2), background_color=bg_color), sg.Input(size=(10, 1), key="Section")],
# # #         [sg.Text("Admission Number: ", size=(buffer, 2), background_color=bg_color), sg.Input(size = (10, 1), key="Admission Number")],
# # #         [sg.Text("Subject: ", size=(buffer, 2), background_color=bg_color), sg.Input(size=(10, 1), key="Subject")],
# # #         [sg.Text("No of Questions: ", size=(buffer, 2), background_color=bg_color), sg.Input(size=(5, 1), default_text=str(questions) , placeholder=str(questions), enable_events=True ,key="No of Questions"), sg.Button("+", key="INCREMENT", button_color=("#FFFFFF", "#2b2a33")), sg.Button("-", key="DECREMENT", button_color=("#FFFFFF", "#2b2a33"))],
# # #
# # #         [sg.Text("File: ", size=(buffer, 2), background_color=bg_color), sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("csv Files", "*.csv"), ("All Files", "*.*")))],
# # #
# # #         [sg.Button("Generate", key="Submit", button_color=("#FFFFFF", "#2b2a33")), sg.Button("Clear", key="-CLEAR-", button_color=("#FFFFFF", "#2b2a33")) ,sg.Cancel(button_color=("#FFFFFF", "#2b2a33"))],
# # #         [sg.Text("", size=(70, 2), justification="center", background_color=bg_color)],
# # #
# # #     ]
# # #
# # #
# # #     Window = sg.Window("OMR GENERATION FORM", layout, background_color=bg_color)
# # #
# # #     while True:
# # #         event, values = Window.read()
# # #
# # #         if event == sg.WIN_CLOSED:
# # #             break
# # #
# # #         elif event == "Submit":
# # #             if not values["-FILE-"]:
# # #                 values["MODE"] = "single"
# # #
# # #                 if not questions:
# # #                     sg.popup_error("No questions entered", title="Enter Questions")
# # #
# # #                 else:
# # #                     return values
# # #
# # #             else:
# # #                 csv_file = values["-FILE-"]
# # #
# # #                 # ==========================
# # #                 # CSV MODE
# # #                 # ==========================
# # #
# # #                 if csv_file:
# # #
# # #                     if not os.path.exists(csv_file):
# # #                         sg.popup_error("CSV file does not exist.")
# # #                         continue
# # #
# # #                     return {
# # #                         "mode": "csv",
# # #                         "csv_file": csv_file
# # #                     }
# # #
# # #                 # ==========================
# # #                 # SINGLE STUDENT MODE
# # #                 # ==========================
# # #
# # #                 if not questions:
# # #                     sg.popup_error(
# # #                         "No questions entered",
# # #                         title="Enter Questions"
# # #                     )
# # #                     continue
# # #
# # #                 return {
# # #                     **values,
# # #                     "mode": "single"
# # #                 }
# # #
# # #
# # #
# # #         elif event == "-CLEAR-":
# # #             for key, element in Window.key_dict.items():
# # #                 if isinstance(element, sg.Input):
# # #                     element.update("")
# # #
# # #                     questions = 0
# # #
# # #
# # #         elif event == "Cancel":
# # #             break
# # #
# # #
# # #         try:
# # #             if event == "INCREMENT":
# # #                 questions += 1
# # #
# # #             elif event == "DECREMENT":
# # #                 if questions >= 1:
# # #                     questions -= 1
# # #
# # #             elif event == "No of Questions":
# # #                 questions = int(values["No of Questions"])
# # #
# # #
# # #             Window["No of Questions"].update(questions)
# # #
# # #         except ValueError:
# # #             ...
# # #
# # #     Window.close()
# # #
# # #
# # # if __name__ == "__main__":
# # #     print(OMR_generation_form())
# # from json import __main__
# #
# # import PySimpleGUI as sg
# # import os
# #
# #
# # def OMR_generation_form():
# #
# #     bg_color = "#212121"
# #     button_color = "#2b2a33"
# #     buffer = 20
# #     questions = 0
# #
# #     layout = [
# #
# #         [sg.Text(
# #             "OMR GENERATOR",
# #             size=(70, 2),
# #             justification="center",
# #             background_color=bg_color,
# #             font=("Helvetica", 16, "bold")
# #         )],
# #
# #         # -------------------------
# #         # Student information
# #         # -------------------------
# #
# #         [sg.Text(
# #             "Name: ",
# #             size=(buffer, 2),
# #             background_color=bg_color
# #         ),
# #         sg.Input(key="Name")],
# #
# #         [sg.Text(
# #             "Class: ",
# #             size=(buffer, 2),
# #             background_color=bg_color
# #         ),
# #         sg.Input(size=(10, 1), key="Class")],
# #
# #         [sg.Text(
# #             "Section: ",
# #             size=(buffer, 2),
# #             background_color=bg_color
# #         ),
# #         sg.Input(size=(10, 1), key="Section")],
# #
# #         [sg.Text(
# #             "Admission Number: ",
# #             size=(buffer, 2),
# #             background_color=bg_color
# #         ),
# #         sg.Input(size=(10, 1), key="Admission Number")],
# #
# #         [sg.Text(
# #             "Subject: ",
# #             size=(buffer, 2),
# #             background_color=bg_color
# #         ),
# #         sg.Input(key="Subject")],
# #
# #         [sg.Text(
# #             "No of Questions: ",
# #             size=(buffer, 2),
# #             background_color=bg_color
# #         ),
# #         sg.Input(
# #             size=(5, 1),
# #             default_text="0",
# #             enable_events=True,
# #             key="No of Questions"
# #         ),
# #         sg.Button(
# #             "+",
# #             key="INCREMENT",
# #             button_color=("#FFFFFF", button_color)
# #         ),
# #         sg.Button(
# #             "-",
# #             key="DECREMENT",
# #             button_color=("#FFFFFF", button_color)
# #         )],
# #
# #         # -------------------------
# #         # CSV
# #         # -------------------------
# #
# #         [
# #             sg.Text(
# #                 "CSV File: ",
# #                 size=(buffer, 2),
# #                 background_color=bg_color
# #             ),
# #
# #             sg.Input(
# #                 key="-FILE-",
# #                 enable_events=True
# #             ),
# #
# #             sg.FileBrowse(
# #                 file_types=(
# #                     ("CSV Files", "*.csv"),
# #                     ("All Files", "*.*")
# #                 )
# #             )
# #         ],
# #
# #         # -------------------------
# #         # Buttons
# #         # -------------------------
# #
# #         [
# #             sg.Button(
# #                 "Generate",
# #                 key="Submit",
# #                 button_color=("#FFFFFF", button_color)
# #             ),
# #
# #             sg.Button(
# #                 "Clear",
# #                 key="-CLEAR-",
# #                 button_color=("#FFFFFF", button_color)
# #             ),
# #
# #             sg.Cancel(
# #                 button_color=("#FFFFFF", button_color)
# #             )
# #         ],
# #
# #         [
# #             sg.Text(
# #                 "",
# #                 size=(70, 2),
# #                 justification="center",
# #                 background_color=bg_color
# #             )
# #         ],
# #     ]
# #
# #     window = sg.Window(
# #         "OMR GENERATION FORM",
# #         layout,
# #         background_color=bg_color
# #     )
# #
# #     while True:
# #
# #         event, values = window.read()
# #
# #         if event == sg.WIN_CLOSED:
# #             break
# #
# #         # =========================================================
# #         # GENERATE
# #         # =========================================================
# #
# #         elif event == "Submit":
# #
# #             csv_file = values["-FILE-"].strip()
# #
# #             # -----------------------------------------------------
# #             # CSV MODE
# #             # -----------------------------------------------------
# #
# #             if csv_file:
# #
# #                 if not os.path.isfile(csv_file):
# #
# #                     sg.popup_error(
# #                         "The selected CSV file does not exist.",
# #                         title="Invalid CSV"
# #                     )
# #
# #                     continue
# #
# #                 return {
# #                     "mode": "csv",
# #                     "csv_file": csv_file
# #                 }
# #
# #             # -----------------------------------------------------
# #             # SINGLE STUDENT MODE
# #             # -----------------------------------------------------
# #
# #             if questions <= 0:
# #
# #                 sg.popup_error(
# #                     "No questions entered.",
# #                     title="Enter Questions"
# #                 )
# #
# #                 continue
# #
# #             values["mode"] = "single"
# #
# #             return values
# #
# #         # =========================================================
# #         # CLEAR
# #         # =========================================================
# #
# #         elif event == "-CLEAR-":
# #
# #             for key, element in window.key_dict.items():
# #
# #                 if isinstance(element, sg.Input):
# #
# #                     element.update("")
# #
# #             questions = 0
# #
# #             window["No of Questions"].update("0")
# #
# #         # =========================================================
# #         # CANCEL
# #         # =========================================================
# #
# #         elif event == "Cancel":
# #
# #             break
# #
# #         # =========================================================
# #         # QUESTION COUNTER
# #         # =========================================================
# #
# #         try:
# #
# #             if event == "INCREMENT":
# #
# #                 questions += 1
# #
# #             elif event == "DECREMENT":
# #
# #                 if questions > 0:
# #                     questions -= 1
# #
# #             elif event == "No of Questions":
# #
# #                 questions = int(
# #                     values["No of Questions"]
# #                 )
# #
# #                 if questions < 0:
# #                     questions = 0
# #
# #             window["No of Questions"].update(
# #                 questions
# #             )
# #
# #         except ValueError:
# #
# #             pass
# #
# #     window.close()
# #
# #
# # if __name__ == "__main__":
# #     print(OMR_generation_form())
#
# import PySimpleGUI as sg
# import os
#
#
# def OMR_generation_form():
#
#     bg_color = "#212121"
#     button_color = "#2b2a33"
#     buffer = 20
#
#     questions = 0
#
#     single_fields = [
#         "Name",
#         "Class",
#         "Section",
#         "Admission Number",
#         "Subject",
#         "No of Questions"
#     ]
#
#     layout = [
#
#         [sg.Text("OMR GENERATOR", size=(70, 2), justification="center", background_color=bg_color, font=("Helvetica", 16, "bold"))],
#
#         [sg.Text("Name: ", size=(buffer, 2), background_color=bg_color), sg.Input(key="Name", enable_events=True)],
#
#         [sg.Text("Class: ",size=(buffer, 2),background_color=bg_color),
#             sg.Input(size=(10, 1),key="Class",enable_events=True)
#          ],
#
#         [sg.Text("Section: ",size=(buffer, 2),background_color=bg_color),
#             sg.Input(size=(10, 1),key="Section",enable_events=True)
#          ],
#
#         [sg.Text("Admission Number: ",size=(buffer, 2),background_color=bg_color),
#             sg.Input(size=(10, 1),key="Admission Number",enable_events=True)
#          ],
#
#         [sg.Text("Subject: ",size=(buffer, 2),background_color=bg_color),
#             sg.Input(key="Subject",enable_events=True)
#          ],
#
#         [sg.Text("No of Questions: ",size=(buffer, 2),background_color=bg_color),
#             sg.Input(size=(5, 1),default_text="0",key="No of Questions",enable_events=True),
#             sg.Button("+",key="INCREMENT",button_color=("#FFFFFF", button_color)),
#             sg.Button("-",key="DECREMENT",button_color=("#FFFFFF", button_color))
#          ],
#
#         [sg.Text("CSV File: ",size=(buffer, 2),background_color=bg_color),
#             sg.Input(key="-FILE-",enable_events=True),
#             sg.FileBrowse(file_types=(("CSV Files", "*.csv"),("All Files", "*.*")))
#          ],
#
#         [sg.Button("Generate",key="Submit",button_color=("#FFFFFF", button_color)),
#             sg.Button("Clear",key="-CLEAR-",button_color=("#FFFFFF", button_color)),
#             sg.Cancel(button_color=("#FFFFFF", button_color))
#          ],
#
#         [sg.Text("",size=(70, 2),justification="center",background_color=bg_color)]
#     ]
#
#     window = sg.Window("OMR GENERATION FORM",layout,background_color=bg_color)
#
#     # ============================================================
#     # Update which input source is active
#     # ============================================================
#
#     def update_input_state(values):
#
#         # Check whether CSV has been selected
#         has_csv = bool(
#             str(values["-FILE-"]).strip()
#         )
#
#         # Check whether any manual field contains data
#         has_single_data = any(
#             str(values[key]).strip()
#             for key in single_fields
#             if key != "No of Questions"
#         )
#
#         # Question count also counts as manual input
#         question_text = str(
#             values["No of Questions"]
#         ).strip()
#
#         if question_text and question_text != "0":
#             has_single_data = True
#
#         # --------------------------------------------------------
#         # CSV selected
#         # --------------------------------------------------------
#
#         if has_csv:
#
#             for key in single_fields:
#                 window[key].update(disabled=True)
#
#             window["INCREMENT"].update(disabled=True)
#             window["DECREMENT"].update(disabled=True)
#
#         # --------------------------------------------------------
#         # Manual student data entered
#         # --------------------------------------------------------
#
#         elif has_single_data:
#
#             window["-FILE-"].update(disabled=True)
#
#         # --------------------------------------------------------
#         # Nothing entered
#         # --------------------------------------------------------
#
#         else:
#
#             window["-FILE-"].update(disabled=False)
#
#             for key in single_fields:
#                 window[key].update(disabled=False)
#
#             window["INCREMENT"].update(disabled=False)
#             window["DECREMENT"].update(disabled=False)
#
#     # ============================================================
#     # Event loop
#     # ============================================================
#
#     while True:
#
#         event, values = window.read()
#
#         if event == sg.WIN_CLOSED:
#             break
#
#         # ========================================================
#         # GENERATE
#         # ========================================================
#
#         elif event == "Submit":
#
#             csv_file = str(
#                 values["-FILE-"]
#             ).strip()
#
#             # ----------------------------------------------------
#             # CSV MODE
#             # ----------------------------------------------------
#
#             if csv_file:
#
#                 if not os.path.isfile(csv_file):
#
#                     sg.popup_error(
#                         "The selected CSV file does not exist.",
#                         title="Invalid CSV"
#                     )
#
#                     continue
#
#                 return {
#                     "mode": "csv",
#                     "csv_file": csv_file
#                 }
#
#             # ----------------------------------------------------
#             # SINGLE STUDENT MODE
#             # ----------------------------------------------------
#
#             if questions <= 0:
#
#                 sg.popup_error(
#                     "No questions entered.",
#                     title="Enter Questions"
#                 )
#
#                 continue
#
#             values["mode"] = "single"
#
#             return values
#
#         # ========================================================
#         # CLEAR
#         # ========================================================
#
#         elif event == "-CLEAR-":
#
#             for key in single_fields:
#
#                 window[key].update("")
#
#             window["-FILE-"].update("")
#
#             questions = 0
#
#             window[
#                 "No of Questions"
#             ].update("0")
#
#             update_input_state(values)
#
#         # ========================================================
#         # CANCEL
#         # ========================================================
#
#         elif event == "Cancel":
#
#             break
#
#         # ========================================================
#         # CSV changed
#         # ========================================================
#
#         elif event == "-FILE-":
#
#             update_input_state(values)
#
#         # ========================================================
#         # Manual input changed
#         # ========================================================
#
#         elif event in single_fields:
#
#             update_input_state(values)
#
#         # ========================================================
#         # Increment questions
#         # ========================================================
#
#         elif event == "INCREMENT":
#
#             questions += 1
#
#             window[
#                 "No of Questions"
#             ].update(questions)
#
#             update_input_state(values)
#
#         # ========================================================
#         # Decrement questions
#         # ========================================================
#
#         elif event == "DECREMENT":
#
#             if questions > 0:
#                 questions -= 1
#
#             window[
#                 "No of Questions"
#             ].update(questions)
#
#             update_input_state(values)
#
#         # ========================================================
#         # Question input manually changed
#         # ========================================================
#
#         elif event == "No of Questions":
#
#             try:
#
#                 questions = int(
#                     values["No of Questions"]
#                 )
#
#                 if questions < 0:
#                     questions = 0
#
#                 window[
#                     "No of Questions"
#                 ].update(questions)
#
#             except ValueError:
#
#                 questions = 0
#
#                 window[
#                     "No of Questions"
#                 ].update("0")
#
#             update_input_state(values)
#
#     window.close()
#
#
# if __name__ == "__main__":
#     OMR_generation_form()


import csv
import io
import json
import os
import re
import sys
import time
import PySimpleGUI as sg
from Generators import OMRGenerator

from PIL import Image


# ============================================================
# DEFAULT CONFIG
# ============================================================

CONFIG = {

    "page_size": "A4",

    "orientation": "Portrait",

    "questions": 80,

    "choices": (
        "A",
        "B",
        "C",
        "D"
    ),

    "name": "Student",

    "class_standard": "XII",

    "class_division": "A",

    "admission_number": "0000",

    "subject": "Physics",

    "margin": 100,

    "header_height": 470,

    "start_y": 560,

    "bottom_margin": 180,

    "question_spacing": 105,

    "column_gap": 70,

    "bubble_spacing": 150,

    "bubble_radius": 24,

    "question_bubble_gap": 35,

    "qr_enabled": True,

    "qr_position": "Top Right",

    "output_format": "PDF",

    "header_name": True,

    "header_class": True,

    "header_section": True,

    "header_admission": True,

    "header_subject": True,
}


# ============================================================
# GUI THEME
# ============================================================

BG = "#000000"

BUTTON_BG = "#212121"

FG = "#FFFFFF"

SECONDARY_FG = "#BDBDBD"


sg.theme(
    "Black"
)


sg.set_options(

    font=(
        "Arial",
        10
    ),

    background_color=BG,

    element_background_color=BG,

    text_color=FG,

    input_text_color=FG,

    input_elements_background_color=(
        BUTTON_BG
    ),

    button_color=(
        FG,
        BUTTON_BG
    ),
)


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(
    value,
    default
):

    try:

        value = str(
            value
        ).strip()

        if not value:

            return default

        return int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        return default


# ============================================================
# MAKE GENERATOR
# ============================================================

def make_generator(
    values,
    candidate=None
):

    config = CONFIG.copy()

    config["page_size"] = values.get(
        "page_size",
        CONFIG["page_size"]
    )

    config["orientation"] = values.get(
        "orientation",
        CONFIG["orientation"]
    )

    config["questions"] = max(
        1,

        safe_int(
            values.get(
                "questions"
            ),

            CONFIG[
                "questions"
            ]
        )
    )

    options = max(
        2,

        min(
            6,

            safe_int(
                values.get(
                    "options"
                ),

                4
            )
        )
    )

    config["choices"] = tuple(
        "ABCDEF"[
            :options
        ]
    )

    candidate = (
        candidate
        or {}
    )

    config["name"] = str(
        candidate.get(
            "name",
            values.get(
                "name",
                CONFIG["name"]
            )
        )
    ).strip()

    config[
        "class_standard"
    ] = str(
        candidate.get(
            "class_standard",
            values.get(
                "class_standard",
                CONFIG[
                    "class_standard"
                ]
            )
        )
    ).strip()

    config[
        "class_division"
    ] = str(
        candidate.get(
            "class_division",
            values.get(
                "section",
                CONFIG[
                    "class_division"
                ]
            )
        )
    ).strip()

    config[
        "admission_number"
    ] = str(
        candidate.get(
            "admission_number",
            values.get(
                "admission",
                CONFIG[
                    "admission_number"
                ]
            )
        )
    ).strip()

    config[
        "subject"
    ] = str(
        candidate.get(
            "subject",
            values.get(
                "subject",
                CONFIG[
                    "subject"
                ]
            )
        )
    ).strip()

    config[
        "column_gap"
    ] = max(
        1,

        safe_int(
            values.get(
                "column_gap"
            ),

            CONFIG[
                "column_gap"
            ]
        )
    )

    config[
        "bubble_spacing"
    ] = max(
        1,

        safe_int(
            values.get(
                "bubble_spacing"
            ),

            CONFIG[
                "bubble_spacing"
            ]
        )
    )

    config[
        "bubble_radius"
    ] = max(
        1,

        safe_int(
            values.get(
                "bubble_radius"
            ),

            CONFIG[
                "bubble_radius"
            ]
        )
    )

    config[
        "question_spacing"
    ] = max(
        1,

        safe_int(
            values.get(
                "question_spacing"
            ),

            CONFIG[
                "question_spacing"
            ]
        )
    )

    config[
        "margin"
    ] = max(
        1,

        safe_int(
            values.get(
                "margin"
            ),

            CONFIG[
                "margin"
            ]
        )
    )

    config[
        "qr_enabled"
    ] = bool(
        values.get(
            "qr_enabled",
            CONFIG[
                "qr_enabled"
            ]
        )
    )

    config[
        "qr_position"
    ] = values.get(
        "qr_position",
        CONFIG[
            "qr_position"
        ]
    )

    config[
        "output_format"
    ] = values.get(
        "output_format",
        CONFIG[
            "output_format"
        ]
    )

    config[
        "header_name"
    ] = bool(
        values.get(
            "header_name"
        )
    )

    config[
        "header_class"
    ] = bool(
        values.get(
            "header_class"
        )
    )

    config[
        "header_section"
    ] = bool(
        values.get(
            "header_section"
        )
    )

    config[
        "header_admission"
    ] = bool(
        values.get(
            "header_admission"
        )
    )

    config[
        "header_subject"
    ] = bool(
        values.get(
            "header_subject"
        )
    )

    return OMRGenerator(
        config
    )


# ============================================================
# CSV STUDENT IMPORT
# ============================================================

CSV_REQUIRED_COLUMNS = {

    "name": "name",

    "class": "class_standard",

    "section": "class_division",

    "admission": "admission_number",

    "subject": "subject",
}


def normalize_csv_header(
    header
):

    header = str(
        header
    ).strip().lower()

    header = re.sub(
        r"[^a-z0-9]+",
        "_",
        header
    )

    return header.strip(
        "_"
    )


def load_student_csv(
    filename
):

    if not filename:

        raise ValueError(
            "No CSV file was selected."
        )

    with open(
        filename,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        if not reader.fieldnames:

            raise ValueError(
                "The CSV file has no header row."
            )

        normalized_headers = {

            normalize_csv_header(
                header
            ): header

            for header in reader.fieldnames

            if header is not None
        }

        missing = [

            required

            for required
            in CSV_REQUIRED_COLUMNS

            if required
            not in normalized_headers
        ]

        if missing:

            raise ValueError(

                "Missing required CSV "
                "column(s): "

                + ", ".join(
                    missing
                )

                + "\n\nRequired columns:\n"

                "Name, Class, Section, "
                "Admission, Subject"
            )

        students = []

        seen_admissions = set()

        for row_number, row in enumerate(
            reader,
            start=2
        ):

            if not any(
                str(
                    value
                    or ""
                ).strip()

                for value
                in row.values()
            ):

                continue

            student = {

                "name": str(
                    row.get(
                        normalized_headers[
                            "name"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "class_standard": str(
                    row.get(
                        normalized_headers[
                            "class"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "class_division": str(
                    row.get(
                        normalized_headers[
                            "section"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "admission_number": str(
                    row.get(
                        normalized_headers[
                            "admission"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "subject": str(
                    row.get(
                        normalized_headers[
                            "subject"
                        ],
                        ""
                    )
                    or ""
                ).strip(),
            }

            missing_values = [

                field

                for field, value
                in student.items()

                if not value
            ]

            if missing_values:

                raise ValueError(
                    f"Row {row_number} "
                    f"is incomplete. "
                    f"Missing: "
                    + ", ".join(
                        missing_values
                    )
                )

            admission_key = (
                student[
                    "admission_number"
                ].casefold()
            )

            if admission_key in seen_admissions:

                raise ValueError(
                    "Duplicate admission "
                    "number found: "
                    f"{student['admission_number']} "
                    f"(row {row_number})"
                )

            seen_admissions.add(
                admission_key
            )

            students.append(
                student
            )

    if not students:

        raise ValueError(
            "The CSV file contains no "
            "student records."
        )

    return students


def sanitize_filename(
    value
):

    value = str(
        value
    ).strip()

    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value
    )

    return (
        value.strip("._")
        or "Candidate"
    )


# ============================================================
# GUI SETTINGS
# ============================================================

settings = [

    [
        sg.Frame(
            "📄 Page",
            [

                [
                    sg.Text(
                        "Size",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "A4",
                            "A5",
                            "A3",
                            "Letter",
                            "Legal"
                        ],

                        default_value="A4",

                        key="page_size",

                        readonly=True,

                        enable_events=True,

                        size=(12, 1)
                    )
                ],

                [
                    sg.Text(
                        "Orientation",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "Portrait",
                            "Landscape"
                        ],

                        default_value="Portrait",

                        key="orientation",

                        readonly=True,

                        enable_events=True,

                        size=(12, 1)
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📝 Questions",
            [

                [
                    sg.Text(
                        "No. questions",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "80",

                        key="questions",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Options",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "2",
                            "3",
                            "4",
                            "5",
                            "6"
                        ],

                        default_value="4",

                        readonly=True,

                        key="options",

                        enable_events=True,

                        size=(12, 1)
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "⚪ Layout",
            [

                [
                    sg.Text(
                        "Bubble radius",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "24",

                        key="bubble_radius",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Bubble spacing",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "150",

                        key="bubble_spacing",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Question spacing",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "105",

                        key="question_spacing",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Column gap",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "70",

                        key="column_gap",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Margin",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "100",

                        key="margin",

                        size=(12, 1),

                        enable_events=True
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📥 Candidate Source",
            [

                [
                    sg.Radio(
                        "Manual",
                        "candidate_source",

                        default=True,

                        key="input_mode_manual",

                        enable_events=True
                    ),

                    sg.Radio(
                        "CSV",
                        "candidate_source",

                        default=False,

                        key="input_mode_csv",

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "CSV file",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "",

                        key="csv_file",

                        size=(30, 1),

                        readonly=True
                    ),

                    sg.Button(
                        "Load CSV",

                        key="load_csv",

                        size=(12, 1),

                        font=(
                            "Arial",
                            10
                        ),

                        button_color=(
                            FG,
                            BUTTON_BG
                        ),

                        disabled=True
                    )
                ],

                [
                    sg.Text(
                        "Candidate",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [],

                        key="csv_candidate",

                        size=(30, 1),

                        readonly=True,

                        enable_events=True,

                        disabled=True
                    )
                ],

                [
                    sg.Text(
                        "CSV format:",
                        size=(16, 1)
                    ),

                    sg.Text(
                        "Name, Class, Section, Admission, Subject",

                        text_color=(
                            SECONDARY_FG
                        )
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "👤 Student Information",
            [

                [
                    sg.Text(
                        "Name",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "Student",

                        key="name",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Class",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "XII",

                        key="class_standard",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Section",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "A",

                        key="section",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Admission",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "0000",

                        key="admission",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Subject",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "Physics",

                        key="subject",

                        size=(20, 1),

                        enable_events=True
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "🔲 QR",
            [

                [
                    sg.Checkbox(
                        "Enable QR",

                        default=True,

                        key="qr_enabled",

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Position",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "Top Left",
                            "Top Right",
                            "Bottom Left",
                            "Bottom Right"
                        ],

                        default_value="Top Right",

                        readonly=True,

                        key="qr_position",

                        enable_events=True,

                        size=(15, 1)
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📋 Header",
            [

                [
                    sg.Checkbox(
                        "Name",

                        default=True,

                        key="header_name",

                        enable_events=True
                    ),

                    sg.Checkbox(
                        "Class",

                        default=True,

                        key="header_class",

                        enable_events=True
                    )
                ],

                [
                    sg.Checkbox(
                        "Section",

                        default=True,

                        key="header_section",

                        enable_events=True
                    ),

                    sg.Checkbox(
                        "Admission No.",

                        default=True,

                        key="header_admission",

                        enable_events=True
                    )
                ],

                [
                    sg.Checkbox(
                        "Subject",

                        default=True,

                        key="header_subject",

                        enable_events=True
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📤 Output",
            [

                [
                    sg.Text(
                        "Format",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "PDF",
                            "PNG",
                            "JPG",
                            "JPEG"
                        ],

                        default_value="PDF",

                        key="output_format",

                        readonly=True,

                        enable_events=True,

                        size=(15, 1)
                    )
                ],

                [
                    sg.Text(
                        "PDF:",
                        size=(16, 1)
                    ),

                    sg.Text(
                        "One multi-page file",

                        text_color=(
                            SECONDARY_FG
                        )
                    )
                ],

                [
                    sg.Text(
                        "PNG/JPG:",
                        size=(16, 1)
                    ),

                    sg.Text(
                        "One file per page",

                        text_color=(
                            SECONDARY_FG
                        )
                    )
                ]
            ],

            expand_x=True
        )
    ]
]


# ============================================================
# MAIN LAYOUT
# ============================================================

layout = [

    [
        sg.Text(
            "OMR SHEET GENERATOR",

            font=(
                "Arial",
                22,
                "bold"
            ),

            justification="center",

            expand_x=True
        )
    ],

    [
        sg.Text(
            "Configure your OMR sheet",

            font=(
                "Arial",
                12
            ),

            text_color=(
                SECONDARY_FG
            ),

            justification="center",

            expand_x=True
        )
    ],

    [
        sg.HorizontalSeparator()
    ],

    [

        sg.Column(
            settings,

            scrollable=True,

            vertical_scroll_only=True,

            size=(
                1000,
                780
            ),

            expand_y=True,

            pad=(
                (5, 15),
                (5, 5)
            )
        ),

        sg.VSeparator(),

        sg.Column(
            [

                [
                    sg.Text(
                        "LIVE PREVIEW",

                        font=(
                            "Arial",
                            16,
                            "bold"
                        ),

                        justification="center",

                        expand_x=True
                    )
                ],

                [
                    sg.Image(
                        key="preview",

                        size=(
                            800,
                            900
                        ),

                        background_color="#333333",

                        expand_x=True,

                        expand_y=True
                    )
                ],

                [
                    sg.Button(
                        "◀ Previous",

                        key="previous_page",

                        size=(14, 2),

                        font=(
                            "Arial",
                            10
                        ),

                        button_color=(
                            FG,
                            BUTTON_BG
                        ),

                        disabled=True
                    ),

                    sg.Text(
                        "Page 1 of 1",

                        key="page_info",

                        text_color=FG,

                        justification="center",

                        size=(16, 1)
                    ),

                    sg.Button(
                        "Next ▶",

                        key="next_page",

                        size=(14, 2),

                        font=(
                            "Arial",
                            10
                        ),

                        button_color=(
                            FG,
                            BUTTON_BG
                        ),

                        disabled=True
                    )
                ],

                [
                    sg.Text(
                        "Loading preview...",

                        key="layout_info",

                        text_color=(
                            SECONDARY_FG
                        ),

                        justification="center",

                        expand_x=True
                    )
                ]
            ],

            expand_x=True,

            expand_y=True,

            justification="center",

            element_justification="center"
        )
    ],

    [
        sg.HorizontalSeparator()
    ],

    [
        sg.Button(
            "Load Template",

            key="load_template",

            size=(15, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Button(
            "Save Template",

            size=(15, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Button(
            "Generate",

            size=(15, 2),

            font=(
                "Arial",
                10,
                "bold"
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Button(
            "Reset",

            size=(15, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Push(),

        sg.Button(
            "Exit",

            size=(10, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        )
    ]
]


# ============================================================
# WINDOW
# ============================================================

window = sg.Window(

    "OMR Generator",

    layout,

    size=(
        1950,
        1500
    ),

    resizable=True,

    finalize=True
)


# ============================================================
# CANDIDATE STATE
# ============================================================

csv_students = []

csv_candidate_labels = []


# ============================================================
# PREVIEW STATE
# ============================================================

preview_pages = []

preview_page_index = 0


# ============================================================
# SHOW PREVIEW PAGE
# ============================================================

def show_preview_page():

    global preview_page_index

    if not preview_pages:

        return

    preview_page_index = max(
        0,

        min(
            preview_page_index,

            len(preview_pages) - 1
        )
    )

    page = preview_pages[
        preview_page_index
    ].copy()

    page.thumbnail(
        (
            800,
            900
        ),

        Image.Resampling.LANCZOS
    )

    buffer = io.BytesIO()

    page.save(
        buffer,
        format="PNG"
    )

    window[
        "preview"
    ].update(
        data=buffer.getvalue()
    )

    window[
        "page_info"
    ].update(
        f"Page "
        f"{preview_page_index + 1}"
        f" of "
        f"{len(preview_pages)}"
    )

    window[
        "previous_page"
    ].update(
        disabled=(
            preview_page_index <= 0
        )
    )

    window[
        "next_page"
    ].update(
        disabled=(
            preview_page_index
            >= len(preview_pages) - 1
        )
    )


# ============================================================
# UPDATE PREVIEW
# ============================================================

def update_preview(
    values
):

    global preview_pages
    global preview_page_index

    try:

        candidate = None

        selected_index = 0

        if values.get(
            "input_mode_csv"
        ):

            if not csv_students:

                window[
                    "layout_info"
                ].update(

                    "Load a CSV file "
                    "to preview candidates...",

                    text_color="#FF9800"
                )

                return

            selected_label = values.get(
                "csv_candidate",
                ""
            )

            try:

                selected_index = (
                    csv_candidate_labels.index(
                        selected_label
                    )
                )

            except ValueError:

                selected_index = 0

            candidate = (
                csv_students[
                    selected_index
                ]
            )

        generator = make_generator(
            values,
            candidate
        )

        preview_pages = (
            generator.generate()
        )

        preview_page_index = 0

        show_preview_page()

        if candidate is None:

            candidate_info = (
                "Manual candidate"
            )

        else:

            candidate_info = (

                f"Candidate "
                f"{selected_index + 1}"
                f" of "
                f"{len(csv_students)}"
                f"  |  "
                f"{candidate['name']}"
                f"  | Admission "
                f"{candidate['admission_number']}"
            )

        window[
            "layout_info"
        ].update(

            f"{candidate_info}"
            f"  |  "
            f"{len(preview_pages)}"
            f" page(s)"
            f"  |  "
            f"{generator.get_questions_per_column()}"
            f" questions/column"
            f"  |  "
            f"{generator.get_max_columns()}"
            f" max columns"
            f"  |  "
            f"Template "
            f"{generator.template_id}"
        )

    except Exception as error:

        window[
            "layout_info"
        ].update(

            "Preview waiting for "
            "valid settings...",

            text_color="#FF9800"
        )

        print(
            "Preview error:",
            error
        )


# ============================================================
# CANDIDATE SOURCE UI
# ============================================================

def update_candidate_source_ui(
    values
):

    manual_mode = bool(
        values.get(
            "input_mode_manual",
            True
        )
    )

    csv_mode = not manual_mode

    manual_keys = [

        "name",

        "class_standard",

        "section",

        "admission",

        "subject",
    ]

    for key in manual_keys:

        window[
            key
        ].update(
            disabled=csv_mode
        )

    window[
        "load_csv"
    ].update(
        disabled=not csv_mode
    )

    window[
        "csv_candidate"
    ].update(

        values=csv_candidate_labels,

        value=(

            csv_candidate_labels[0]

            if csv_students

            else ""
        ),

        disabled=(
            not csv_mode
        )
        or not csv_students
    )


# ============================================================
# LOAD CSV INTO GUI
# ============================================================

def load_csv_into_gui(
    filename
):

    global csv_students

    global csv_candidate_labels

    students = load_student_csv(
        filename
    )

    csv_students = students

    csv_candidate_labels = [

        (
            f"{student['admission_number']}"
            f" — "
            f"{student['name']}"
        )

        for student in students
    ]

    window[
        "csv_file"
    ].update(
        value=filename
    )

    window[
        "csv_candidate"
    ].update(

        values=csv_candidate_labels,

        value=csv_candidate_labels[0],

        disabled=False
    )

    return students


# ============================================================
# INITIAL PREVIEW
# ============================================================

event, values = window.read(
    timeout=50
)

if event != sg.WIN_CLOSED:

    update_candidate_source_ui(
        values
    )

    update_preview(
        values
    )


# ============================================================
# PREVIEW DEBOUNCE
# ============================================================

preview_pending = False

preview_deadline = 0


# ============================================================
# LOAD TEMPLATE
# ============================================================

def load_template():

    filename = sg.popup_get_file(

        "Load OMR template",

        file_types=(

            (
                "JSON Files",
                "*.json"
            ),
        )
    )

    if not filename:

        return None

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            template = json.load(
                file
            )

        if not isinstance(
            template,
            dict
        ):

            raise ValueError(
                "Template file must contain "
                "a JSON object."
            )

        return template

    except (
        OSError,
        json.JSONDecodeError,
        ValueError
    ) as error:

        sg.popup_error(

            "Could not load template:\n\n"
            f"{error}"
        )

        return None


# ============================================================
# EVENT LOOP
# ============================================================

while True:

    event, values = window.read(
        timeout=50
    )

    if event in (
        sg.WIN_CLOSED,
        "Exit"
    ):

        break

    # ========================================================
    # MANUAL / CSV MODE
    # ========================================================

    if event in (
        "input_mode_manual",
        "input_mode_csv"
    ):

        update_candidate_source_ui(
            values
        )

        preview_pending = True

        preview_deadline = (
            time.monotonic()
            + 0.05
        )

    # ========================================================
    # LOAD CSV
    # ========================================================

    if event == "load_csv":

        try:

            filename = sg.popup_get_file(

                "Select student CSV",

                file_types=(

                    (
                        "CSV Files",
                        "*.csv"
                    ),

                    (
                        "All Files",
                        "*.*"
                    )
                )
            )

            if filename:

                students = (
                    load_csv_into_gui(
                        filename
                    )
                )

                window[
                    "input_mode_csv"
                ].update(
                    value=True
                )

                window[
                    "input_mode_manual"
                ].update(
                    value=False
                )

                current_values = (
                    window.read(
                        timeout=0
                    )[1]
                )

                update_candidate_source_ui(
                    current_values
                )

                update_preview(
                    current_values
                )

                sg.popup(

                    f"Loaded "
                    f"{len(students)} "
                    f"candidate(s).",

                    title="CSV Loaded"
                )

        except Exception as error:

            sg.popup_error(

                "Could not load CSV:\n\n"
                f"{error}"
            )

    # ========================================================
    # CSV CANDIDATE SELECTION
    # ========================================================

    if event == "csv_candidate":

        update_preview(
            values
        )

    # ========================================================
    # PREVIOUS PAGE
    # ========================================================

    if event == "previous_page":

        if preview_page_index > 0:

            preview_page_index -= 1

            show_preview_page()

    # ========================================================
    # NEXT PAGE
    # ========================================================

    if event == "next_page":

        if (
            preview_page_index
            < len(preview_pages) - 1
        ):

            preview_page_index += 1

            show_preview_page()

    # ========================================================
    # SETTINGS CHANGED
    # ========================================================

    if (

        event

        not in (
            sg.TIMEOUT_EVENT,
            None
        )

        and event

        not in (
            "Generate",
            "Save Template",
            "Reset",
            "load_template",
            "load_csv",
            "csv_candidate",
            "input_mode_manual",
            "input_mode_csv",
            "previous_page",
            "next_page"
        )
    ):

        preview_pending = True

        preview_deadline = (
            time.monotonic()
            + 0.20
        )

    # ========================================================
    # DEBOUNCED PREVIEW
    # ========================================================

    if (

        preview_pending

        and time.monotonic()
        >= preview_deadline
    ):

        update_preview(
            values
        )

        preview_pending = False

    # ========================================================
    # LOAD TEMPLATE
    # ========================================================

    if event == "load_template":

        template = load_template()

        if template is not None:

            try:

                for key, value in (
                    template.items()
                ):

                    if (
                        key
                        in window.AllKeysDict
                    ):

                        window[
                            key
                        ].update(
                            value
                        )

                _, restored_values = (
                    window.read(
                        timeout=0
                    )
                )

                update_candidate_source_ui(
                    restored_values
                )

                if restored_values.get(
                    "input_mode_csv"
                ):

                    csv_filename = (
                        restored_values.get(
                            "csv_file",
                            ""
                        )
                    )

                    if (

                        csv_filename

                        and os.path.exists(
                            csv_filename
                        )
                    ):

                        try:

                            load_csv_into_gui(
                                csv_filename
                            )

                            restored_values = (
                                window.read(
                                    timeout=0
                                )[1]
                            )

                        except Exception as csv_error:

                            sg.popup_error(

                                "Template loaded, "
                                "but its CSV file "
                                "could not be loaded:\n\n"
                                f"{csv_error}"
                            )

                update_preview(
                    restored_values
                )

                preview_pending = False

                sg.popup(

                    "Template loaded successfully!",

                    title="OMR Template"
                )

            except Exception as error:

                sg.popup_error(

                    "Could not apply template:\n\n"
                    f"{error}"
                )

    # ========================================================
    # GENERATE
    # ========================================================

    if event == "Generate":

        try:

            output_format = str(
                values.get(
                    "output_format",
                    "PDF"
                )
            ).strip().upper()

            if output_format not in {

                "PDF",
                "PNG",
                "JPG",
                "JPEG"
            }:

                raise ValueError(
                    "Please select a valid "
                    "output format."
                )

            # ------------------------------------------------
            # Candidate source
            # ------------------------------------------------

            if values.get(
                "input_mode_csv"
            ):

                if not csv_students:

                    raise ValueError(

                        "CSV mode is selected, "
                        "but no student CSV "
                        "has been loaded."
                    )

                candidates = (
                    csv_students
                )

            else:

                candidates = [

                    {

                        "name": values.get(
                            "name",
                            ""
                        ),

                        "class_standard": values.get(
                            "class_standard",
                            ""
                        ),

                        "class_division": values.get(
                            "section",
                            ""
                        ),

                        "admission_number": values.get(
                            "admission",
                            ""
                        ),

                        "subject": values.get(
                            "subject",
                            ""
                        ),
                    }
                ]

            # ------------------------------------------------
            # Validate candidates
            # ------------------------------------------------

            for (
                candidate_index,
                candidate
            ) in enumerate(
                candidates,
                start=1
            ):

                missing = [

                    field

                    for field, value
                    in candidate.items()

                    if not str(
                        value
                    ).strip()
                ]

                if missing:

                    raise ValueError(

                        f"Candidate "
                        f"{candidate_index} "
                        f"is missing: "

                        + ", ".join(
                            missing
                        )
                    )

            # ------------------------------------------------
            # Output folder
            # ------------------------------------------------

            folder = sg.popup_get_folder(
                "Select output folder"
            )

            if folder:

                generated_count = 0

                for candidate in candidates:

                    generator = make_generator(
                        values,
                        candidate
                    )

                    generator.generate()

                    safe_admission = (
                        sanitize_filename(
                            candidate[
                                "admission_number"
                            ]
                        )
                    )

                    safe_name = (
                        sanitize_filename(
                            candidate[
                                "name"
                            ]
                        )
                    )

                    prefix = os.path.join(

                        folder,

                        (
                            "OMR_"
                            f"{safe_admission}_"
                            f"{safe_name}"
                        )
                    )

                    generator.save_output(
                        output_format,
                        prefix
                    )

                    generated_count += 1

                sg.popup(

                    f"Generated sheets for "
                    f"{generated_count} "
                    f"candidate(s).\n\n"

                    f"Format: "
                    f"{output_format}",

                    title="OMR Generated"
                )

        except Exception as error:

            sg.popup_error(

                "Generation failed:\n\n"
                f"{error}"
            )

    # ========================================================
    # SAVE TEMPLATE
    # ========================================================

    if event == "Save Template":

        try:

            filename = sg.popup_get_file(

                "Save OMR template",

                save_as=True,

                default_extension=".json",

                file_types=(

                    (
                        "JSON Files",
                        "*.json"
                    ),

                    (
                        "All Files",
                        "*.*"
                    ),
                )
            )

            if filename:

                if not filename.lower().endswith(
                    ".json"
                ):

                    filename += ".json"

                config = values.copy()

                with open(
                    filename,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(

                        config,

                        file,

                        indent=4
                    )

                sg.popup(

                    "Template saved "
                    "successfully!\n\n"
                    f"{filename}",

                    title="OMR Template"
                )

        except Exception as error:

            sg.popup_error(

                "Could not save template:\n\n"
                f"{error}"
            )

    # ========================================================
    # RESET
    # ========================================================

    if event == "Reset":

        answer = sg.popup_yes_no(
            "Reset the generator?"
        )

        if answer == "Yes":

            window.close()

            os.execl(

                sys.executable,

                sys.executable,

                *sys.argv
            )


# ============================================================
# CLOSE
# ============================================================

window.close()