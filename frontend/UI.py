from tkinter import *
from functions import create_project_window
from sidebar import create_sidebar
from projects import create_projects_page
from assets import asset_path
from project_action import create_project_action_window
from omr_generator import create_omr_generator_page
import requests


def create_project(project_window, project_name, question_count):
    data = {
        "name": project_name,
        "question_count": question_count
    }

    response = requests.post(
        "http://127.0.0.1:8080/api/v1/projects",
        json=data
    )

    print("Backend response:", response.status_code)
    print(response.json())


def start_scan(event=None):
    global action_page, current_project
    preview_project = {
        "name": "Physics Test",
        "question_count": 50,
    }
    current_project = preview_project
    dashboard_frame.pack_forget()
    projects_page.pack_forget()
    action_page = create_project_action_window(content_frame, preview_project, show_projects, show_generator)
    action_page.pack(side="left", fill="both", expand=True)
    # Later:
    # open file dialog / camera / scanning screen

def card_enter(event=None):
    project_card.config(highlightbackground="#3A3F46")

def card_leave(event=None):
    project_card.config(highlightbackground="#2A2F36")
def show_dashboard():
    hide_extra_pages()
    projects_page.pack_forget()
    dashboard_frame.pack(
        side="left",
        fill="both",
        expand=True
    )


def show_projects():
    hide_extra_pages()
    # Hide the dashboard
    dashboard_frame.pack_forget()

    # Show the Projects page
    projects_page.pack(
        side="left",
        fill="both",
        expand=True
    )


def show_generator(project=None):
    global current_project
    if project is not None:
        current_project = project
    dashboard_frame.pack_forget()
    projects_page.pack_forget()
    hide_extra_pages()
    generator_page.set_project(current_project)
    generator_page.pack(side="left", fill="both", expand=True)


def hide_extra_pages():
    if action_page is not None:
        action_page.pack_forget()
    if generator_page is not None:
        generator_page.pack_forget()


window = Tk()

window.title("OMR Scanify")    #App name
window.geometry("1280x720")
icon = PhotoImage(file=asset_path("omricon.png"))
card_image = PhotoImage(file=asset_path("foldericon.png"))   #folder icon of card
card_image = card_image.subsample(11, 11)  # Resize the image to 1/3 of its original size
window.iconphoto(True, icon)

window.config(background="black")
action_page = None
generator_page = None
current_project = {"name": "Physics Test", "question_count": 50}
sidebar = create_sidebar(window, show_dashboard, show_projects, show_generator)    #created a sidebar using the create_sidebar function from sidebar.py

content_frame = Frame(window, bg="black")
content_frame.pack(side="left", fill="both", expand=True)

dashboard_frame = Frame(content_frame, bg="black")
dashboard_frame.pack(side="left", fill="both", expand=True)

projects_page = create_projects_page(content_frame, start_scan)
generator_page = create_omr_generator_page(content_frame, current_project, on_back=show_projects)

label= Label(dashboard_frame,   # added a label for the dashboard title
             text="Dashboard" , 
             font=('Segoe UI', 26 , 'bold' ), 
             fg='white', 
             bg='black')

label.place(x=60, y=75)

dashsubtitle= Label(dashboard_frame,   # added a label for the dashboard subtitle
             text="Create and manage OMR projects with ease." ,
                font=('Segoe UI', 14),
                fg='#A7A7A7',
                bg='black')
dashsubtitle.place(x=62, y=120)

project=Label(dashboard_frame,     # added a label for the project section
             text="Project" ,
             font=('Segoe UI', 16, 'bold'),
             fg='#FFFFFF',
             bg='black')
project.place(x=60, y=190)

project_card = Frame(    # added a frame for the project card
    dashboard_frame,
    bg="#15181D",
    highlightbackground="#2A2F36",
    highlightthickness=1,
    
)


project_card.place(    #place the project card frame on the window
    x=60,
    y=225,
    width=900,
    height=150
)
project_card.bind("<Button-1>", start_scan)   #bind the click event to the frame

card_title = Label(   # added a label for the project card title
    project_card,
    text="Create a New Project",
    font=('Segoe UI', 18, 'bold'),
    fg='#FFFFFF',
    bg='#15181D',
    padx=150,
)

card_title.place(x=180, y=20)
card_title.place(x=25, y=20)

card_image_label = Label(       # added a label for the project card image
    project_card,
    image=card_image,
    bg='#15181D'
)

card_image_label.place(x=25, y=20)

card_subtitle = Label(             # added a label for the project card subtitle
    project_card,
    text="Start a new OMR project to manage answer sheets, answer keys, and generated OMRs.",
    font=('Segoe UI', 11),
    fg='#A9AFB8',
    bg='#15181D',
    padx=10
)
card_subtitle.place(x=180, y=60)

card_title.bind("<Button-1>", start_scan)         #bind the click event to the title label
card_subtitle.bind("<Button-1>", start_scan)        #bind the click event to the subtitle label
card_image_label.bind("<Button-1>", start_scan)     #bind the click event to the image label
project_card.bind("<Enter>", card_enter)
project_card.bind("<Leave>", card_leave)

card_title.bind("<Enter>", card_enter)
card_title.bind("<Leave>", card_leave)

card_subtitle.bind("<Enter>", card_enter)
card_subtitle.bind("<Leave>", card_leave)

card_image_label.bind("<Enter>", card_enter)
card_image_label.bind("<Leave>", card_leave)






window.mainloop()