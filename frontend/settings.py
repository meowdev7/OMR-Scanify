import tkinter as tk

from theme import PALETTES, resolve_theme


def create_settings_page(parent, mode, on_theme_changed):
    page = tk.Frame(parent)
    page._theme_mode = mode

    def redraw(selected_mode):
        page._theme_mode = selected_mode
        on_theme_changed(selected_mode)
        render()

    def render():
        palette = PALETTES[resolve_theme(page._theme_mode)]
        for child in page.winfo_children():
            child.destroy()
        page.configure(bg=palette["window"])
        tk.Label(page, text="Settings", font=("Segoe UI", 24, "bold"), fg=palette["text"], bg=palette["window"]).pack(anchor="nw", padx=30, pady=(24, 2))
        tk.Label(page, text="Customize your OMR Scanify preferences.", font=("Segoe UI", 10), fg=palette["muted"], bg=palette["window"]).pack(anchor="nw", padx=30)

        appearance = tk.Frame(page, bg=palette["panel"], highlightbackground=palette["border"], highlightthickness=1)
        appearance.pack(fill="x", padx=30, pady=(20, 14), ipadx=14, ipady=14)
        tk.Label(appearance, text="Appearance", font=("Segoe UI", 11, "bold"), fg="#4A99FF", bg=palette["panel"]).pack(anchor="w", padx=14)
        tk.Label(appearance, text="Theme", font=("Segoe UI", 10, "bold"), fg=palette["text"], bg=palette["panel"]).pack(anchor="w", padx=14, pady=(16, 0))
        tk.Label(appearance, text="Choose how OMR Scanify looks.", font=("Segoe UI", 9), fg=palette["muted"], bg=palette["panel"]).pack(anchor="w", padx=14)

        choices = tk.Frame(appearance, bg=palette["panel"])
        choices.pack(fill="x", padx=14, pady=(10, 0))
        for name, title, description in (("dark", "Dark", "Best for low light environments."), ("light", "Light", "Clean and bright experience."), ("system", "System", "Use your system setting.")):
            selected = page._theme_mode == name
            card = tk.Frame(choices, bg=palette["panel_alt"], highlightbackground=palette["blue"] if selected else palette["border"], highlightthickness=2 if selected else 1, cursor="hand2")
            card.pack(side="left", fill="both", expand=True, padx=(0, 10) if name != "system" else 0, ipady=10)
            tk.Label(card, text={"dark": "D", "light": "L", "system": "S"}[name], font=("Segoe UI", 18, "bold"), fg=palette["text"], bg=palette["panel_alt"]).pack(anchor="w", padx=12)
            tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=palette["text"], bg=palette["panel_alt"]).pack(anchor="w", padx=12, pady=(5, 2))
            tk.Label(card, text=description, font=("Segoe UI", 8), fg=palette["muted"], bg=palette["panel_alt"], wraplength=150, justify="left").pack(anchor="w", padx=12)
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda event, value=name: (redraw(value), "break")[1])
            card.bind("<Button-1>", lambda event, value=name: redraw(value))

        about = tk.Frame(page, bg=palette["panel"], highlightbackground=palette["border"], highlightthickness=1)
        about.pack(fill="x", padx=30, pady=(0, 20), ipadx=14, ipady=15)
        tk.Label(about, text="About", font=("Segoe UI", 11, "bold"), fg="#4A99FF", bg=palette["panel"]).pack(anchor="w", padx=14)
        tk.Label(about, text="OMR Scanify", font=("Segoe UI", 13, "bold"), fg=palette["text"], bg=palette["panel"]).pack(anchor="w", padx=14, pady=(14, 0))
        tk.Label(about, text="Version 1.0.0\nOMR Scanify is a modern solution for creating, managing, and scanning OMR answer sheets with ease.", font=("Segoe UI", 9), fg=palette["muted"], bg=palette["panel"], justify="left").pack(anchor="w", padx=14, pady=(3, 0))
        tk.Label(about, text="Copyright 2025 OMR Scanify. All rights reserved.", font=("Segoe UI", 8), fg=palette["muted"], bg=palette["panel"]).pack(anchor="w", padx=14, pady=(18, 0))

    render()
    return page