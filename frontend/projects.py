import tkinter as tk
from tkinter import messagebox, simpledialog
from storage import delete_project, load_projects, rename_project
from assets import asset_path

pro_img = None


def create_projects_page(window, on_create_project=None, on_select_project=None):
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

        try:
            projects = load_projects()
        except Exception as error:
            messagebox.showerror("Projects unavailable", f"Could not load projects from the backend:\n\n{error}", parent=projects_page.winfo_toplevel())
            projects = []

        if projects:
            for project in projects:
                project_card = tk.Frame(
                    project_list,
                    bg="#11151B",
                    highlightbackground="#252B34",
                    highlightthickness=1
                )
                project_card.pack(fill="x", pady=(0, 10), ipady=12)

                select_project = lambda event=None, selected=project: on_select_project(selected) if on_select_project else None
                project_card.bind("<Button-1>", select_project)

                def rename_selected(selected=project):
                    current_name = selected.get("name", "Untitled Project")
                    new_name = simpledialog.askstring(
                        "Rename project",
                        "Project name:",
                        initialvalue=current_name,
                        parent=projects_page.winfo_toplevel(),
                    )
                    if new_name is None or not new_name.strip() or new_name.strip() == current_name:
                        return

                    try:
                        rename_project(selected["id"], new_name.strip())
                    except Exception as error:
                        messagebox.showerror(
                            "Rename failed",
                            f"Could not rename the project:\n\n{error}",
                            parent=projects_page.winfo_toplevel(),
                        )
                        return

                    refresh_projects()

                def delete_selected(selected=project):
                    project_name = selected.get("name", "Untitled Project")
                    confirmed = messagebox.askyesno(
                        "Delete project",
                        f'Delete "{project_name}"? This cannot be undone.',
                        parent=projects_page.winfo_toplevel(),
                    )
                    if not confirmed:
                        return

                    try:
                        delete_project(selected["id"])
                    except Exception as error:
                        messagebox.showerror(
                            "Delete failed",
                            f"Could not delete the project:\n\n{error}",
                            parent=projects_page.winfo_toplevel(),
                        )
                        return

                    refresh_projects()

                project_menu = tk.Menu(
                    projects_page,
                    tearoff=0,
                    bg="#11151B",
                    fg="#E8EDF4",
                    activebackground="#1769E8",
                    activeforeground="#FFFFFF",
                    disabledforeground="#68717D",
                    borderwidth=1,
                    relief="solid",
                    font=("Segoe UI", 9),
                )
                project_menu.add_command(label="Rename", command=rename_selected)
                project_menu.add_command(label="Delete", command=delete_selected)

                menu_button = tk.Button(
                    project_card,
                    text="...",
                    font=("Segoe UI", 11, "bold"),
                    fg="#B9C1CC",
                    bg="#11151B",
                    activeforeground="#FFFFFF",
                    activebackground="#1B222C",
                    relief="flat",
                    bd=0,
                    padx=8,
                    pady=2,
                    cursor="hand2",
                )
                menu_button.pack(side="right", anchor="n", padx=(0, 8), pady=(7, 0))
                menu_button.configure(
                    command=lambda menu=project_menu, button=menu_button: menu.tk_popup(
                        button.winfo_rootx(),
                        button.winfo_rooty() + button.winfo_height(),
                    )
                )

                name_label = tk.Label(
                    project_card,
                    text=project.get("name", "Untitled Project"),
                    font=("Segoe UI", 12, "bold"),
                    fg="#E8EDF4",
                    bg="#11151B"
                )
                name_label.pack(anchor="w", padx=16)
                name_label.bind("<Button-1>", select_project)

                question_count = project.get("question_count", 0)
                student_count = len(project.get("students") or [])
                result_count = len(project.get("results") or [])
                details_label = tk.Label(
                    project_card,
                    text=f"{question_count} questions  |  {student_count} students  |  {result_count} results",
                    font=("Segoe UI", 9),
                    fg="#8B939E",
                    bg="#11151B"
                )
                details_label.pack(anchor="w", padx=16, pady=(4, 0))
                details_label.bind("<Button-1>", select_project)
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