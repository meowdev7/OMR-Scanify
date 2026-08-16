import PySimpleGUI as sg

def OMR_generation_form():
    buffer = 20
    questions = 0
    layout = [
        # [sg.Text("OMR GENERATION FORM", size=(100, 2), justification="center")],
        [sg.Text("Name: ", size=(buffer, 2)), sg.Input(key="Name")],
        [sg.Text("Class: ", size=(buffer, 2)), sg.Input(size=(10, 1), key="Class")],
        [sg.Text("Section", size=(buffer, 2)), sg.Input(size=(10, 1), key="Section")],
        [sg.Text("Admission Number: ", size=(buffer, 2)), sg.Input(size = (10, 1), key="Admission Number")],
        [sg.Text("Subject: ", size=(buffer, 2)), sg.Input(size=(10, 1), key="Subject")],
        [sg.Text("No of Questions: ", size=(buffer, 2)), sg.Input(size=(5, 1), default_text=str(questions) , placeholder=str(questions), enable_events=True ,key="No of Questions"), sg.Button("+", key="INCREMENT"), sg.Button("-", key="DECREMENT")],
        [sg.Button("Generate", key="Submit"), sg.Button("Clear", key="-CLEAR-") ,sg.Cancel()]
    ]


    Window = sg.Window("OMR GENERATION FORM", layout)

    while True:
        event, values = Window.read()

        if event == sg.WIN_CLOSED:
            break

        elif event == "Submit":
            print(values)
            return values

        elif event == "-CLEAR-":
            for key, element in Window.key_dict.items():
                if isinstance(element, sg.Input):
                    element.update("")

                    questions = 0


        elif event == "Cancel":
            break


        try:
            if event == "INCREMENT":
                questions += 1

            elif event == "DECREMENT":
                if questions >= 1:
                    questions -= 1

            elif event == "No of Questions":
                questions = int(values["No of Questions"])


            Window["No of Questions"].update(questions)

        except ValueError:
            ...

    Window.close()


if __name__ == "__main__":
    OMR_generation_form()