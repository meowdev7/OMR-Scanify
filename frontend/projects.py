import tkinter as tk
from storage import load_projects
from assets import asset_path

pro_img = None


def create_projects_page(window, on_create_project=None):
    global pro_img

    pro_img = tk.PhotoImage(file=asset_path("empty_project_img.png")).subsample(5, 5)
    projects_page = tk.Frame(window, bg="#080A0D")

    header = tk.Frame(projects_page, bg="#080A0D")
    header.pack(fill="x", padx=26, pady=(22, 0))

    heading_group = tk.Frame(header, bg="#080A0D")
    heading_group.pack(side="left")

    tk.Label(
        heading_group,
        text="Projects",
        font=("Segoe UI", 25, "bold"),
        fg="#F4F7FB",
        bg="#080A0D"
    ).pack(anchor="w")

    tk.Label(
        heading_group,
        text="View and manage your OMR projects.",
        font=("Segoe UI", 10),
        fg="#8B939E",
        bg="#080A0D"
    ).pack(anchor="w", pady=(2, 0))

    create_button = tk.Button(
        header,
        text="+  New Project",
        font=("Segoe UI", 10, "bold"),
        fg="#FFFFFF",
        bg="#1769E8",
        activeforeground="#FFFFFF",
        activebackground="#2B7CF0",
        relief="flat",
        bd=0,
        padx=13,
        pady=7,
        cursor="hand2",
        command=on_create_project
    )
    create_button.pack(side="right", anchor="n", pady=(9, 0))

    toolbar = tk.Frame(projects_page, bg="#080A0D")
    toolbar.pack(fill="x", padx=26, pady=(21, 0))

    search_frame = tk.Frame(
        toolbar,
        bg="#11151B",
        highlightbackground="#252B34",
        highlightthickness=1
    )
    search_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

    tk.Label(
        search_frame,
        text="?",
        font=("Segoe UI", 11, "bold"),
        fg="#8B939E",
        bg="#11151B"
    ).pack(side="left", padx=(11, 6))

    tk.Entry(
        search_frame,
        font=("Segoe UI", 10),
        fg="#E8EDF4",
        bg="#11151B",
        insertbackground="#FFFFFF",
        relief="flat",
        bd=0
    ).pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 10))

    sort_button = tk.Button(
        toolbar,
        text="Sort by: Recent  v",
        font=("Segoe UI", 9),
        fg="#B9C1CC",
        bg="#0D1116",
        activeforeground="#FFFFFF",
        activebackground="#171D25",
        relief="flat",
        highlightbackground="#252B34",
        highlightthickness=1,
        bd=0,
        padx=12,
        pady=7,
        cursor="hand2"
    )
    sort_button.pack(side="left")

    tk.Button(
        toolbar,
        text="[]",
        font=("Segoe UI", 10, "bold"),
        fg="#3C8BFF",
        bg="#111C2D",
        activeforeground="#FFFFFF",
        activebackground="#172943",
        relief="flat",
        bd=0,
        padx=9,
        pady=6,
        cursor="hand2"
    ).pack(side="left", padx=(12, 4))

    tk.Button(
        toolbar,
        text="=",
        font=("Segoe UI", 11, "bold"),
        fg="#7C8591",
        bg="#0D1116",
        activeforeground="#FFFFFF",
        activebackground="#171D25",
        relief="flat",
        bd=0,
        padx=9,
        pady=6,
        cursor="hand2"
    ).pack(side="left")

    tk.Label(
        projects_page,
        text="Your Projects",
        font=("Segoe UI", 11, "bold"),
        fg="#F4F7FB",
        bg="#080A0D"
    ).pack(anchor="w", padx=26, pady=(20, 8))

    project_list = tk.Frame(projects_page, bg="#080A0D")
    project_list.pack(fill="both", expand=True, padx=26)

    def refresh_projects():
        for child in project_list.winfo_children():
            child.destroy()

        projects = load_projects()

        if projects:
            for project in projects:
                project_card = tk.Frame(
                    project_list,
                    bg="#11151B",
                    highlightbackground="#252B34",
                    highlightthickness=1
                )
                project_card.pack(fill="x", pady=(0, 10), ipady=12)

                tk.Label(
                    project_card,
                    text=project.get("name", "Untitled Project"),
                    font=("Segoe UI", 12, "bold"),
                    fg="#E8EDF4",
                    bg="#11151B"
                ).pack(anchor="w", padx=16)

                question_count = project.get("question_count", 0)
                student_count = len(project.get("students") or [])
                result_count = len(project.get("results") or [])
                tk.Label(
                    project_card,
                    text=f"{question_count} questions  |  {student_count} students  |  {result_count} results",
                    font=("Segoe UI", 9),
                    fg="#8B939E",
                    bg="#11151B"
                ).pack(anchor="w", padx=16, pady=(4, 0))
            return

        empty_state = tk.Frame(
            project_list,
            bg="#090C10",
            highlightbackground="#242A33",
            highlightthickness=1
        )
        empty_state.pack(fill="x", ipady=19)

        illustration = tk.Frame(empty_state, bg="#090C10")
        illustration.pack(pady=(0, 2))

        image_label = tk.Label(illustration, image=pro_img, bg="#090C10")
        image_label.image = pro_img
        image_label.pack()

        tk.Label(
            empty_state,
            text="No projects yet",
            font=("Segoe UI", 13, "bold"),
            fg="#E8EDF4",
            bg="#090C10"
        ).pack(pady=(0, 4))

        tk.Label(
            empty_state,
            text="Create your first OMR project to get started.",
            font=("Segoe UI", 9),
            fg="#8B939E",
            bg="#090C10"
        ).pack()

        tk.Button(
            empty_state,
            text="+  Create New Project",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg="#1769E8",
            activeforeground="#FFFFFF",
            activebackground="#2B7CF0",
            relief="flat",
            bd=0,
            padx=13,
            pady=6,
            cursor="hand2",
            command=on_create_project
        ).pack(pady=(13, 0))

    projects_page.refresh_projects = refresh_projects
    refresh_projects()

    info = tk.Frame(projects_page, bg="#0B1423")
    info.pack(fill="x", padx=26, pady=(13, 0))

    tk.Label(
        info,
        text="i",
        font=("Segoe UI", 9, "bold"),
        fg="#3C8BFF",
        bg="#0B1423"
    ).pack(side="left", padx=(10, 7), pady=8)

    tk.Label(
        info,
        text="Projects you create will appear here. You can upload answer sheets, answer keys, and generate OMRs.",
        font=("Segoe UI", 8),
        fg="#AEB7C5",
        bg="#0B1423",
        anchor="w"
    ).pack(side="left", fill="x", expand=True, pady=8)

    return projects_page