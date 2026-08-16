def card_enter(event):
    quick_scan_card.config(bg="#1C2128")
    card_title.config(bg="#1C2128")
    card_subtitle.config(bg="#1C2128")
    card_image_label.config(bg="#1C2128")


def card_leave(event):
    quick_scan_card.config(bg="#15181D")
    card_title.config(bg="#15181D")
    card_subtitle.config(bg="#15181D")
    card_image_label.config(bg="#15181D")

    def start_scan(event=None):
    # UI action
    open_scan_screen()

    def open_scan_screen():
    # Connect this to your actual OMR backend
    pass