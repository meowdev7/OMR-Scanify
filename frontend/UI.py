from tkinter import *
import requests
from functions import create_project_window
from sidebar import create_sidebar
from projects import create_projects_page
from assets import asset_path
from project_action import create_project_action_window
from project_details import create_project_details_page
from omr_generator import create_omr_generator_page
from settings import create_settings_page
from storage import get_project, load_theme_preference, save_theme_preference
from theme import PALETTES, apply_theme, resolve_theme


def start_scan(event=None):
    dialog = create_project_window(window, on_project_created)
    apply_theme(dialog, theme_mode)


def on_project_created(project):
    global action_page, current_project
    current_project = project
    projects_page.refresh_projects()
    show_project_actions(project)


def show_project_actions(project):
    global action_page, current_project
    try:
        project = get_project(project["id"])
    except (KeyError, requests.RequestException):
        pass
    current_project = project
    dashboard_frame.pack_forget()
    projects_page.pack_forget()
    settings_page.pack_forget()
    hide_extra_pages()
    action_page = create_project_action_window(content_frame, project, show_projects, show_generator, show_project_actions)
    action_page.pack(side="left", fill="both", expand=True)
    apply_theme(window, theme_mode)


def show_project_details(project):
    global current_project, project_details_page
    try:
        project = get_project(project["id"])
    except (KeyError, requests.RequestException):
        pass
    current_project = project
    dashboard_frame.pack_forget()
    projects_page.pack_forget()
    settings_page.pack_forget()
    hide_extra_pages()
    if project_details_page is None:
        project_details_page = create_project_details_page(content_frame, project, lambda: show_project_actions(current_project), show_generator, on_project_updated=on_project_updated)
    else:
        project_details_page.project = project
        project_details_page.destroy()
        project_details_page = create_project_details_page(content_frame, project, lambda: show_project_actions(current_project), show_generator, on_project_updated=on_project_updated)
    project_details_page.pack(side="left", fill="both", expand=True)
    apply_theme(window, theme_mode)

def card_enter(event=None):
    project_card.config(highlightbackground=PALETTES[resolve_theme(theme_mode)]["blue"])

def card_leave(event=None):
    project_card.config(highlightbackground=PALETTES[resolve_theme(theme_mode)]["border"])
def show_dashboard():
    hide_extra_pages()
    projects_page.pack_forget()
    settings_page.pack_forget()
    dashboard_frame.pack(
        side="left",
        fill="both",
        expand=True
    )
    apply_theme(window, theme_mode)


def show_projects():
    hide_extra_pages()
    # Hide the dashboard
    dashboard_frame.pack_forget()
    settings_page.pack_forget()

    # Show the Projects page
    projects_page.pack(
        side="left",
        fill="both",
        expand=True
    )
    apply_theme(window, theme_mode)


def show_settings():
    hide_extra_pages()
    dashboard_frame.pack_forget()
    projects_page.pack_forget()
    settings_page.pack(side="left", fill="both", expand=True)
    apply_theme(window, theme_mode)


def on_theme_changed(mode):
    global theme_mode
    theme_mode = mode
    window._theme_mode = mode
    save_theme_preference(mode)
    apply_theme(window, theme_mode)


def show_generator(project=None):
    global current_project
    if project is not None:
        current_project = project
    dashboard_frame.pack_forget()
    projects_page.pack_forget()
    settings_page.pack_forget()
    hide_extra_pages()
    if generator_page is not None:
        generator_page.set_project(current_project)
    generator_page.pack(side="left", fill="both", expand=True)
    apply_theme(window, theme_mode)


def on_project_updated(project):
    global current_project
    current_project = project
    projects_page.refresh_projects()


def hide_extra_pages():
    if action_page is not None:
        action_page.pack_forget()
    if generator_page is not None:
        generator_page.pack_forget()
    if project_details_page is not None:
        project_details_page.pack_forget()


window = Tk()

window.title("OMR Scanify")    #App name
window.geometry("1280x720")
icon = PhotoImage(file=asset_path("omricon.png"))
card_image = PhotoImage(file=asset_path("foldericon.png"))   #folder icon of card
card_image = card_image.subsample(11, 11)  # Resize the image to 1/3 of its original size
window.iconphoto(True, icon)

window.config(background="black")
theme_mode = load_theme_preference()
window._theme_mode = theme_mode
action_page = None
generator_page = None
project_details_page = None
current_project = None
sidebar = create_sidebar(window, show_dashboard, show_projects, show_settings)

content_frame = Frame(window, bg="black")
content_frame.pack(side="left", fill="both", expand=True)

dashboard_frame = Frame(content_frame, bg="black")
dashboard_frame.pack(side="left", fill="both", expand=True)

projects_page = create_projects_page(content_frame, start_scan, show_project_actions)
generator_page = create_omr_generator_page(
    content_frame,
    current_project,
    on_back=lambda selected_project=None: show_project_actions(selected_project or current_project),
    on_project_updated=on_project_updated,
)
settings_page = create_settings_page(content_frame, theme_mode, on_theme_changed)

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

apply_theme(window, theme_mode)





window.mainloop()