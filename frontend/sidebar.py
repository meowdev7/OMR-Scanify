import tkinter as tk


def create_sidebar(window, show_dashboard, show_projects, show_generator=None):

    # Main sidebar
    sidebar = tk.Frame(
        window,
        bg="#111418",
        width=220
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    # App name
    app_name = tk.Label(
        sidebar,
        text="OMR Scanify",
        font=("Segoe UI", 18, "bold"),
        fg="white",
        bg="#111418"
    )

    app_name.pack(
        pady=(35, 30),
        padx=25,
        anchor="w"
    )

    # -------------------------
    # Navigation button function
    # -------------------------

    def create_nav_button(text,command):

        button = tk.Button(
            sidebar,
            text=text,
            font=("Segoe UI", 11, "bold"),
            fg="#FFFFFF",
            bg="#111418",
            activeforeground="#FFFFFF",
            activebackground="#1C2128",
            relief="flat",
            bd=0,
            anchor="w",
            padx=25,
            cursor="hand2",
            command=command
        )

        button.pack(
            fill="x",
            ipady=7,
            pady=1
        )

        # Hover effect
        def on_enter(event):
            button.config(bg="#1C2128")

        def on_leave(event):
            button.config(bg="#111418")

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    # Dashboard navigation
    dashboard_button = create_nav_button("Dashboard", show_dashboard)

    # Projects navigation
    projects_button = create_nav_button("Projects", show_projects)

    if show_generator is not None:
        create_nav_button("OMR Generator", show_generator)

    return sidebar