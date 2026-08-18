# # import PySimpleGUI as sg
# # import os
# #
# #
# # class CustomText(sg.Text):
# #     """A custom text element with predefined styling."""
# #
# #     def __init__(self, text, *args, **kwargs):
# #         # Define default styles
# #         default_font = ('Helvetica', 12, 'bold')
# #         default_color = '#FFFFFF'
# #         default_bg = '#4A90E2'
# #
# #         # Merge user kwargs with defaults
# #         kwargs['font'] = kwargs.get('font', default_font)
# #         kwargs['text_color'] = kwargs.get('text_color', default_color)
# #         kwargs['background_color'] = kwargs.get('background_color', default_bg)
# #
# #         # Initialize the parent PySimpleGUI Text class
# #         super().__init__(text, *args, **kwargs)
# #
# #
# # def OMR_generation_form():
# #     bg_color = "#212121"
# #     button_color = "#2b2a33"
# #     buffer = 20
# #     questions = 0
# #     layout = [
# #         [sg.Text("", size=(70, 2), justification="center", background_color=bg_color)],
# #
# #         [sg.Text("Name: ", size=(buffer, 2), background_color=bg_color), sg.Input(key="Name")],
# #         [sg.Text("Class: ", size=(buffer, 2), background_color=bg_color), sg.Input(size=(10, 1), key="Class")],
# #         [sg.Text("Section", size=(buffer, 2), background_color=bg_color), sg.Input(size=(10, 1), key="Section")],
# #         [sg.Text("Admission Number: ", size=(buffer, 2), background_color=bg_color), sg.Input(size = (10, 1), key="Admission Number")],
# #         [sg.Text("Subject: ", size=(buffer, 2), background_color=bg_color), sg.Input(size=(10, 1), key="Subject")],
# #         [sg.Text("No of Questions: ", size=(buffer, 2), background_color=bg_color), sg.Input(size=(5, 1), default_text=str(questions) , placeholder=str(questions), enable_events=True ,key="No of Questions"), sg.Button("+", key="INCREMENT", button_color=("#FFFFFF", "#2b2a33")), sg.Button("-", key="DECREMENT", button_color=("#FFFFFF", "#2b2a33"))],
# #
# #         [sg.Text("File: ", size=(buffer, 2), background_color=bg_color), sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("csv Files", "*.csv"), ("All Files", "*.*")))],
# #
# #         [sg.Button("Generate", key="Submit", button_color=("#FFFFFF", "#2b2a33")), sg.Button("Clear", key="-CLEAR-", button_color=("#FFFFFF", "#2b2a33")) ,sg.Cancel(button_color=("#FFFFFF", "#2b2a33"))],
# #         [sg.Text("", size=(70, 2), justification="center", background_color=bg_color)],
# #
# #     ]
# #
# #
# #     Window = sg.Window("OMR GENERATION FORM", layout, background_color=bg_color)
# #
# #     while True:
# #         event, values = Window.read()
# #
# #         if event == sg.WIN_CLOSED:
# #             break
# #
# #         elif event == "Submit":
# #             if not values["-FILE-"]:
# #                 values["MODE"] = "single"
# #
# #                 if not questions:
# #                     sg.popup_error("No questions entered", title="Enter Questions")
# #
# #                 else:
# #                     return values
# #
# #             else:
# #                 csv_file = values["-FILE-"]
# #
# #                 # ==========================
# #                 # CSV MODE
# #                 # ==========================
# #
# #                 if csv_file:
# #
# #                     if not os.path.exists(csv_file):
# #                         sg.popup_error("CSV file does not exist.")
# #                         continue
# #
# #                     return {
# #                         "mode": "csv",
# #                         "csv_file": csv_file
# #                     }
# #
# #                 # ==========================
# #                 # SINGLE STUDENT MODE
# #                 # ==========================
# #
# #                 if not questions:
# #                     sg.popup_error(
# #                         "No questions entered",
# #                         title="Enter Questions"
# #                     )
# #                     continue
# #
# #                 return {
# #                     **values,
# #                     "mode": "single"
# #                 }
# #
# #
# #
# #         elif event == "-CLEAR-":
# #             for key, element in Window.key_dict.items():
# #                 if isinstance(element, sg.Input):
# #                     element.update("")
# #
# #                     questions = 0
# #
# #
# #         elif event == "Cancel":
# #             break
# #
# #
# #         try:
# #             if event == "INCREMENT":
# #                 questions += 1
# #
# #             elif event == "DECREMENT":
# #                 if questions >= 1:
# #                     questions -= 1
# #
# #             elif event == "No of Questions":
# #                 questions = int(values["No of Questions"])
# #
# #
# #             Window["No of Questions"].update(questions)
# #
# #         except ValueError:
# #             ...
# #
# #     Window.close()
# #
# #
# # if __name__ == "__main__":
# #     print(OMR_generation_form())
# from json import __main__
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
#     questions = 0
#
#     layout = [
#
#         [sg.Text(
#             "OMR GENERATOR",
#             size=(70, 2),
#             justification="center",
#             background_color=bg_color,
#             font=("Helvetica", 16, "bold")
#         )],
#
#         # -------------------------
#         # Student information
#         # -------------------------
#
#         [sg.Text(
#             "Name: ",
#             size=(buffer, 2),
#             background_color=bg_color
#         ),
#         sg.Input(key="Name")],
#
#         [sg.Text(
#             "Class: ",
#             size=(buffer, 2),
#             background_color=bg_color
#         ),
#         sg.Input(size=(10, 1), key="Class")],
#
#         [sg.Text(
#             "Section: ",
#             size=(buffer, 2),
#             background_color=bg_color
#         ),
#         sg.Input(size=(10, 1), key="Section")],
#
#         [sg.Text(
#             "Admission Number: ",
#             size=(buffer, 2),
#             background_color=bg_color
#         ),
#         sg.Input(size=(10, 1), key="Admission Number")],
#
#         [sg.Text(
#             "Subject: ",
#             size=(buffer, 2),
#             background_color=bg_color
#         ),
#         sg.Input(key="Subject")],
#
#         [sg.Text(
#             "No of Questions: ",
#             size=(buffer, 2),
#             background_color=bg_color
#         ),
#         sg.Input(
#             size=(5, 1),
#             default_text="0",
#             enable_events=True,
#             key="No of Questions"
#         ),
#         sg.Button(
#             "+",
#             key="INCREMENT",
#             button_color=("#FFFFFF", button_color)
#         ),
#         sg.Button(
#             "-",
#             key="DECREMENT",
#             button_color=("#FFFFFF", button_color)
#         )],
#
#         # -------------------------
#         # CSV
#         # -------------------------
#
#         [
#             sg.Text(
#                 "CSV File: ",
#                 size=(buffer, 2),
#                 background_color=bg_color
#             ),
#
#             sg.Input(
#                 key="-FILE-",
#                 enable_events=True
#             ),
#
#             sg.FileBrowse(
#                 file_types=(
#                     ("CSV Files", "*.csv"),
#                     ("All Files", "*.*")
#                 )
#             )
#         ],
#
#         # -------------------------
#         # Buttons
#         # -------------------------
#
#         [
#             sg.Button(
#                 "Generate",
#                 key="Submit",
#                 button_color=("#FFFFFF", button_color)
#             ),
#
#             sg.Button(
#                 "Clear",
#                 key="-CLEAR-",
#                 button_color=("#FFFFFF", button_color)
#             ),
#
#             sg.Cancel(
#                 button_color=("#FFFFFF", button_color)
#             )
#         ],
#
#         [
#             sg.Text(
#                 "",
#                 size=(70, 2),
#                 justification="center",
#                 background_color=bg_color
#             )
#         ],
#     ]
#
#     window = sg.Window(
#         "OMR GENERATION FORM",
#         layout,
#         background_color=bg_color
#     )
#
#     while True:
#
#         event, values = window.read()
#
#         if event == sg.WIN_CLOSED:
#             break
#
#         # =========================================================
#         # GENERATE
#         # =========================================================
#
#         elif event == "Submit":
#
#             csv_file = values["-FILE-"].strip()
#
#             # -----------------------------------------------------
#             # CSV MODE
#             # -----------------------------------------------------
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
#             # -----------------------------------------------------
#             # SINGLE STUDENT MODE
#             # -----------------------------------------------------
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
#         # =========================================================
#         # CLEAR
#         # =========================================================
#
#         elif event == "-CLEAR-":
#
#             for key, element in window.key_dict.items():
#
#                 if isinstance(element, sg.Input):
#
#                     element.update("")
#
#             questions = 0
#
#             window["No of Questions"].update("0")
#
#         # =========================================================
#         # CANCEL
#         # =========================================================
#
#         elif event == "Cancel":
#
#             break
#
#         # =========================================================
#         # QUESTION COUNTER
#         # =========================================================
#
#         try:
#
#             if event == "INCREMENT":
#
#                 questions += 1
#
#             elif event == "DECREMENT":
#
#                 if questions > 0:
#                     questions -= 1
#
#             elif event == "No of Questions":
#
#                 questions = int(
#                     values["No of Questions"]
#                 )
#
#                 if questions < 0:
#                     questions = 0
#
#             window["No of Questions"].update(
#                 questions
#             )
#
#         except ValueError:
#
#             pass
#
#     window.close()
#
#
# if __name__ == "__main__":
#     print(OMR_generation_form())

import PySimpleGUI as sg
import os


def OMR_generation_form():

    bg_color = "#212121"
    button_color = "#2b2a33"
    buffer = 20

    questions = 0

    single_fields = [
        "Name",
        "Class",
        "Section",
        "Admission Number",
        "Subject",
        "No of Questions"
    ]

    layout = [

        [sg.Text("OMR GENERATOR", size=(70, 2), justification="center", background_color=bg_color, font=("Helvetica", 16, "bold"))],

        [sg.Text("Name: ", size=(buffer, 2), background_color=bg_color), sg.Input(key="Name", enable_events=True)],

        [sg.Text("Class: ",size=(buffer, 2),background_color=bg_color),
            sg.Input(size=(10, 1),key="Class",enable_events=True)
         ],

        [sg.Text("Section: ",size=(buffer, 2),background_color=bg_color),
            sg.Input(size=(10, 1),key="Section",enable_events=True)
         ],

        [sg.Text("Admission Number: ",size=(buffer, 2),background_color=bg_color),
            sg.Input(size=(10, 1),key="Admission Number",enable_events=True)
         ],

        [sg.Text("Subject: ",size=(buffer, 2),background_color=bg_color),
            sg.Input(key="Subject",enable_events=True)
         ],

        [sg.Text("No of Questions: ",size=(buffer, 2),background_color=bg_color),
            sg.Input(size=(5, 1),default_text="0",key="No of Questions",enable_events=True),
            sg.Button("+",key="INCREMENT",button_color=("#FFFFFF", button_color)),
            sg.Button("-",key="DECREMENT",button_color=("#FFFFFF", button_color))
         ],

        [sg.Text("CSV File: ",size=(buffer, 2),background_color=bg_color),
            sg.Input(key="-FILE-",enable_events=True),
            sg.FileBrowse(file_types=(("CSV Files", "*.csv"),("All Files", "*.*")))
         ],

        [sg.Button("Generate",key="Submit",button_color=("#FFFFFF", button_color)),
            sg.Button("Clear",key="-CLEAR-",button_color=("#FFFFFF", button_color)),
            sg.Cancel(button_color=("#FFFFFF", button_color))
         ],

        [sg.Text("",size=(70, 2),justification="center",background_color=bg_color)]
    ]

    window = sg.Window("OMR GENERATION FORM",layout,background_color=bg_color)

    # ============================================================
    # Update which input source is active
    # ============================================================

    def update_input_state(values):

        # Check whether CSV has been selected
        has_csv = bool(
            str(values["-FILE-"]).strip()
        )

        # Check whether any manual field contains data
        has_single_data = any(
            str(values[key]).strip()
            for key in single_fields
            if key != "No of Questions"
        )

        # Question count also counts as manual input
        question_text = str(
            values["No of Questions"]
        ).strip()

        if question_text and question_text != "0":
            has_single_data = True

        # --------------------------------------------------------
        # CSV selected
        # --------------------------------------------------------

        if has_csv:

            for key in single_fields:
                window[key].update(disabled=True)

            window["INCREMENT"].update(disabled=True)
            window["DECREMENT"].update(disabled=True)

        # --------------------------------------------------------
        # Manual student data entered
        # --------------------------------------------------------

        elif has_single_data:

            window["-FILE-"].update(disabled=True)

        # --------------------------------------------------------
        # Nothing entered
        # --------------------------------------------------------

        else:

            window["-FILE-"].update(disabled=False)

            for key in single_fields:
                window[key].update(disabled=False)

            window["INCREMENT"].update(disabled=False)
            window["DECREMENT"].update(disabled=False)

    # ============================================================
    # Event loop
    # ============================================================

    while True:

        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        # ========================================================
        # GENERATE
        # ========================================================

        elif event == "Submit":

            csv_file = str(
                values["-FILE-"]
            ).strip()

            # ----------------------------------------------------
            # CSV MODE
            # ----------------------------------------------------

            if csv_file:

                if not os.path.isfile(csv_file):

                    sg.popup_error(
                        "The selected CSV file does not exist.",
                        title="Invalid CSV"
                    )

                    continue

                return {
                    "mode": "csv",
                    "csv_file": csv_file
                }

            # ----------------------------------------------------
            # SINGLE STUDENT MODE
            # ----------------------------------------------------

            if questions <= 0:

                sg.popup_error(
                    "No questions entered.",
                    title="Enter Questions"
                )

                continue

            values["mode"] = "single"

            return values

        # ========================================================
        # CLEAR
        # ========================================================

        elif event == "-CLEAR-":

            for key in single_fields:

                window[key].update("")

            window["-FILE-"].update("")

            questions = 0

            window[
                "No of Questions"
            ].update("0")

            update_input_state(values)

        # ========================================================
        # CANCEL
        # ========================================================

        elif event == "Cancel":

            break

        # ========================================================
        # CSV changed
        # ========================================================

        elif event == "-FILE-":

            update_input_state(values)

        # ========================================================
        # Manual input changed
        # ========================================================

        elif event in single_fields:

            update_input_state(values)

        # ========================================================
        # Increment questions
        # ========================================================

        elif event == "INCREMENT":

            questions += 1

            window[
                "No of Questions"
            ].update(questions)

            update_input_state(values)

        # ========================================================
        # Decrement questions
        # ========================================================

        elif event == "DECREMENT":

            if questions > 0:
                questions -= 1

            window[
                "No of Questions"
            ].update(questions)

            update_input_state(values)

        # ========================================================
        # Question input manually changed
        # ========================================================

        elif event == "No of Questions":

            try:

                questions = int(
                    values["No of Questions"]
                )

                if questions < 0:
                    questions = 0

                window[
                    "No of Questions"
                ].update(questions)

            except ValueError:

                questions = 0

                window[
                    "No of Questions"
                ].update("0")

            update_input_state(values)

    window.close()


if __name__ == "__main__":
    OMR_generation_form()