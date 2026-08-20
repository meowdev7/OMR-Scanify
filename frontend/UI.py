from tkinter import *
from functions import create_project_window
from sidebar import create_sidebar
import requests


def create_project(project_window, project_name, question_count):
    data = {
        "name": project_name,
        "question_count": question_count
    }

    response = requests.post(
        "http://127.0.0.1:8000/api/v1/projects",
        json=data
    )

    print("Backend response:", response.status_code)
    print(response.json())


def start_scan(event=None):
    create_project_window(window)
    # Later:
    # open file dialog / camera / scanning screen

def card_enter(event=None):
    project_card.config(highlightbackground="#3A3F46")

def card_leave(event=None):
    project_card.config(highlightbackground="#2A2F36")

window = Tk()

window.title("OMR Scanify")    #App name
window.geometry("1280x720")
icon = PhotoImage(file='frontend/omricon.png')
card_image = PhotoImage(file=r'frontend/foldericon.png')   #folder icon of card
card_image = card_image.subsample(11, 11)  # Resize the image to 1/3 of its original size
window.iconphoto(True, icon)

window.config(background="black")
sidebar = create_sidebar(window)    #created a sidebar using the create_sidebar function from sidebar.py

label= Label(window,   # added a label for the dashboard title
             text="Dashboard" , 
             font=('Segoe UI', 26 , 'bold' ), 
             fg='white', 
             bg='black')

label.place(x=280 , y=75)

dashsubtitle= Label(window,   # added a label for the dashboard subtitle
             text="Create and manage OMR projects with ease." ,
                font=('Segoe UI', 14),
                fg='#A7A7A7',
                bg='black')
dashsubtitle.place(x=282 , y=120)

project=Label(window,     # added a label for the project section
             text="Project" ,
             font=('Segoe UI', 16, 'bold'),
             fg='#FFFFFF',
             bg='black')
project.place(x=280, y=190)

project_card = Frame(    # added a frame for the project card
    window,
    bg="#15181D",
    highlightbackground="#2A2F36",
    highlightthickness=1,
    
)


project_card.place(    #place the project card frame on the window
    x=280,
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