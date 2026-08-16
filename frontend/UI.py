from tkinter import *

def start_scan(event=None):
    print("Starting new scan...")
    # Later:
    # open file dialog / camera / scanning screen

def card_enter(event=None):
    quick_scan_card.config(highlightbackground="#3A3F46")

def card_leave(event=None):
    quick_scan_card.config(highlightbackground="#2A2F36")

window = Tk()

window.title("OMR Scanify")
window.geometry("1280x720")
icon = PhotoImage(file='omricon.png')
card_image = PhotoImage(file=r'E:\OneDrive\Documents\card.png')
card_image = card_image.subsample(11, 11)  # Resize the image to 1/3 of its original size
window.iconphoto(True, icon)

window.config(background="black")

label= Label(window,
             text="Dashboard" , 
             font=('Segoe UI', 26 , 'bold' ), 
             fg='white', 
             bg='black')

label.place(x=280 , y=75)

dashsubtitle= Label(window,
             text="Scan and analyze standard OMR answer sheets quickly and accurately" ,
                font=('Segoe UI', 14),
                fg='#A7A7A7',
                bg='black')
dashsubtitle.place(x=282 , y=120)

quickscan=Label(window,
             text="New Project" ,
             font=('Segoe UI', 16, 'bold'),
             fg='#FFFFFF',
             bg='black')
quickscan.place(x=280, y=190)

quick_scan_card = Frame(
    window,
    bg="#15181D",
    highlightbackground="#2A2F36",
    highlightthickness=1,
    
)


quick_scan_card.place(
    x=280,
    y=225,
    width=900,
    height=150
)
quick_scan_card.bind("<Button-1>", start_scan)

card_title = Label(
    quick_scan_card,
    text="Start a New Scan",
    font=('Segoe UI', 18, 'bold'),
    fg='#FFFFFF',
    bg='#15181D',
    padx=150,
)

card_title.place(x=180, y=20)
card_title.place(x=25, y=20)

card_image_label = Label(
    quick_scan_card,
    image=card_image,
    bg='#15181D'
)

card_image_label.place(x=25, y=20)

card_subtitle = Label(
    quick_scan_card,
    text="Upload or Capture an OMR Answer Sheet to begin analysis.",
    font=('Segoe UI', 11),
    fg='#A9AFB8',
    bg='#15181D',
    padx=10
)
card_subtitle.place(x=180, y=60)

card_title.bind("<Button-1>", start_scan)
card_subtitle.bind("<Button-1>", start_scan)
card_image_label.bind("<Button-1>", start_scan)
quick_scan_card.bind("<Enter>", card_enter)
quick_scan_card.bind("<Leave>", card_leave)

card_title.bind("<Enter>", card_enter)
card_title.bind("<Leave>", card_leave)

card_subtitle.bind("<Enter>", card_enter)
card_subtitle.bind("<Leave>", card_leave)

card_image_label.bind("<Enter>", card_enter)
card_image_label.bind("<Leave>", card_leave)



window.mainloop()