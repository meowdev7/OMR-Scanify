import os
import sys
import threading
from pathlib import Path

import PySimpleGUI as sg


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

if str(BASE_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(BASE_DIR)
    )


# ============================================================
# SCANNER ENGINE
# ============================================================

from Scanner.OMR_scanner import (
    find_input_files,
    scan_input,
    SUPPORTED_EXTENSIONS,
)


# ============================================================
# DEFAULT DIRECTORIES
# ============================================================

DEFAULT_INPUT = (
    BASE_DIR / "Input"
)

DEFAULT_TEMPLATES = (
    BASE_DIR / "Templates"
)

DEFAULT_JSON_OUTPUT = (
    BASE_DIR / "Output" / "json"
)

DEFAULT_DEBUG_OUTPUT = (
    BASE_DIR / "Output" / "debug"
)


# ============================================================
# COLORS
# ============================================================

BG = "#000000"
PANEL = "#111111"
BUTTON_BG = "#212121"

FG = "#FFFFFF"
SECONDARY = "#BDBDBD"

SUCCESS = "#66BB6A"
WARNING = "#FFA726"
ERROR = "#EF5350"


# ============================================================
# THEME
# ============================================================

sg.theme("Black")

sg.set_options(

    font=(
        "Arial",
        10
    ),

    background_color=BG,

    element_background_color=BG,

    text_color=FG,

    input_text_color=FG,

    input_elements_background_color=BUTTON_BG,

    button_color=(
        FG,
        BUTTON_BG
    )
)


# ============================================================
# FUNCTIONS
# ============================================================

def get_input_files(
    path
):

    path = Path(
        path
    )

    if not path.exists():

        return []

    try:

        return find_input_files(
            path
        )

    except Exception:

        return []


# ============================================================
# FILE DESCRIPTION
# ============================================================

def describe_files(
    files
):

    if not files:

        return "No supported files found."

    counts = {}

    for file in files:

        extension = (
            file.suffix.lower()
        )

        counts[
            extension
        ] = (
            counts.get(
                extension,
                0
            )
            + 1
        )

    parts = []

    for extension in sorted(
        counts
    ):

        parts.append(
            f"{counts[extension]} "
            f"{extension}"
        )

    return (
        f"{len(files)} file(s)  |  "
        + ", ".join(parts)
    )


# ============================================================
# INPUT INFO
# ============================================================

def update_input_info(
    path
):

    files = get_input_files(
        path
    )

    if files:

        window[
            "-INPUT_INFO-"
        ].update(

            describe_files(
                files
            ),

            text_color=SUCCESS
        )

    else:

        window[
            "-INPUT_INFO-"
        ].update(

            "No supported PNG/JPG/JPEG/PDF files found.",

            text_color=WARNING
        )

    return files


# ============================================================
# BROWSE INPUT
# ============================================================

def browse_input(
    directory_mode
):

    if directory_mode:

        selected = sg.popup_get_folder(

            "Select OMR input directory",

            default_path=str(
                DEFAULT_INPUT
            )
        )

    else:

        selected = sg.popup_get_file(

            "Select OMR input file",

            default_path=str(
                DEFAULT_INPUT
            ),

            file_types=(

                (
                    "OMR files",
                    "*.png;*.jpg;*.jpeg;*.pdf"
                ),

                (
                    "PNG",
                    "*.png"
                ),

                (
                    "JPEG",
                    "*.jpg;*.jpeg"
                ),

                (
                    "PDF",
                    "*.pdf"
                ),

                (
                    "All files",
                    "*.*"
                )
            )
        )

    if selected:

        window[
            "-INPUT-"
        ].update(
            selected
        )

        update_input_info(
            selected
        )


# ============================================================
# BROWSE FOLDER
# ============================================================

def browse_folder(
    key,
    title,
    default_path
):

    selected = sg.popup_get_folder(

        title,

        default_path=str(
            default_path
        )
    )

    if selected:

        window[
            key
        ].update(
            selected
        )


# ============================================================
# LOG
# ============================================================

def log(
    text
):

    window[
        "-LOG-"
    ].print(
        text
    )


# ============================================================
# ENABLE/DISABLE SCANNER CONTROLS
# ============================================================

def set_running(
    running
):

    disabled = bool(
        running
    )

    window[
        "-SCAN-"
    ].update(
        disabled=disabled
    )

    window[
        "-MODE_FILE-"
    ].update(
        disabled=disabled
    )

    window[
        "-MODE_DIR-"
    ].update(
        disabled=disabled
    )

    window[
        "-BROWSE_INPUT-"
    ].update(
        disabled=disabled
    )

    window[
        "-BROWSE_TEMPLATES-"
    ].update(
        disabled=disabled
    )

    window[
        "-BROWSE_JSON-"
    ].update(
        disabled=disabled
    )

    window[
        "-BROWSE_DEBUG-"
    ].update(
        disabled=disabled
    )

    window[
        "-TEMPLATE_ID-"
    ].update(
        disabled=disabled
    )


# ============================================================
# VALIDATE
# ============================================================

def validate(
    values
):

    input_path = Path(
        values.get(
            "-INPUT-",
            ""
        )
    )

    if not input_path.exists():

        raise ValueError(
            "Input file/directory does not exist."
        )

    files = get_input_files(
        input_path
    )

    if not files:

        raise ValueError(
            "No supported input files were found."
        )

    template_path = Path(
        values.get(
            "-TEMPLATES-",
            ""
        )
    )

    if not template_path.is_dir():

        raise ValueError(
            "Templates directory does not exist:\n"
            f"{template_path}"
        )

    json_path = Path(
        values.get(
            "-JSON-OUTPUT-",
            ""
        )
    )

    if not str(
        json_path
    ).strip():

        raise ValueError(
            "JSON output directory is empty."
        )

    debug_path = Path(
        values.get(
            "-DEBUG-OUTPUT-",
            ""
        )
    )

    if not str(
        debug_path
    ).strip():

        raise ValueError(
            "Debug output directory is empty."
        )

    template_id = (
        values.get(
            "-TEMPLATE_ID-",
            ""
        )
        .strip()
    )

    if not template_id:

        template_id = None

    return {

        "input": input_path,

        "files": files,

        "templates": template_path,

        "json": json_path,

        "debug": debug_path,

        "template_id": template_id,

        "debug_enabled": bool(
            values.get(
                "-DEBUG_ENABLED-",
                True
            )
        ),
    }


# ============================================================
# SCAN THREAD
# ============================================================

def scan_worker(
    settings
):

    try:

        settings[
            "json"
        ].mkdir(
            parents=True,
            exist_ok=True
        )

        settings[
            "debug"
        ].mkdir(
            parents=True,
            exist_ok=True
        )

        window.write_event_value(
            "-STATUS_EVENT-",
            {
                "type": "status",
                "text": (
                    f"Scanning "
                    f"{len(settings['files'])} "
                    f"file(s)..."
                )
            }
        )

        result = scan_input(

            input_path=(
                settings[
                    "input"
                ]
            ),

            output_directory=(
                settings[
                    "json"
                ]
            ),

            debug_directory=(
                settings[
                    "debug"
                ]
            ),

            templates_directory=(
                settings[
                    "templates"
                ]
            ),

            forced_template_id=(
                settings[
                    "template_id"
                ]
            )
        )

        window.write_event_value(
            "-SCAN_FINISHED-",
            result
        )

    except Exception as error:

        window.write_event_value(
            "-SCAN_FAILED-",
            str(
                error
            )
        )


# ============================================================
# START SCAN
# ============================================================

def start_scan(
    values
):

    try:

        settings = validate(
            values
        )

    except Exception as error:

        sg.popup_error(

            "Cannot start scanner:\n\n"
            f"{error}",

            title="OMR Scanner"
        )

        return

    window[
        "-LOG-"
    ].update(
        ""
    )

    log(
        "========================================"
    )

    log(
        "OMR SCANNER"
    )

    log(
        "========================================"
    )

    log(
        f"Input: {settings['input']}"
    )

    log(
        f"Files: {len(settings['files'])}"
    )

    log(
        f"Templates: {settings['templates']}"
    )

    log(
        f"JSON output: {settings['json']}"
    )

    log(
        f"Debug output: {settings['debug']}"
    )

    log(
        "----------------------------------------"
    )

    window[
        "-PROGRESS-"
    ].update(
        0,
        max=len(
            settings[
                "files"
            ]
        )
    )

    window[
        "-STATUS-"
    ].update(
        "Scanning...",
        text_color=WARNING
    )

    set_running(
        True
    )

    thread = threading.Thread(

        target=scan_worker,

        args=(
            settings,
        ),

        daemon=True
    )

    thread.start()


# ============================================================
# HANDLE FINISHED
# ============================================================

def handle_finished(
    results
):

    set_running(
        False
    )

    successful = sum(

        1

        for item in results

        if item.get(
            "success",
            False
        )
    )

    total = len(
        results
    )

    failed = (
        total
        - successful
    )

    pages = sum(

        item.get(
            "pages",
            0
        )

        for item in results
    )

    # --------------------------------------------------------
    # Progress is per input file.
    # --------------------------------------------------------

    window[
        "-PROGRESS-"
    ].update(
        total
    )

    if failed:

        window[
            "-STATUS-"
        ].update(

            (
                f"Finished with errors: "
                f"{successful}/{total} "
                f"files"
            ),

            text_color=WARNING
        )

    else:

        window[
            "-STATUS-"
        ].update(

            (
                f"Completed: "
                f"{successful} file(s), "
                f"{pages} page(s)"
            ),

            text_color=SUCCESS
        )

    log(
        ""
    )

    log(
        "========================================"
    )

    log(
        "SCAN COMPLETE"
    )

    log(
        f"Files: {total}"
    )

    log(
        f"Successful: {successful}"
    )

    log(
        f"Failed: {failed}"
    )

    log(
        f"Pages: {pages}"
    )

    log(
        "========================================"
    )

    for item in results:

        status = (
            "OK"
            if item.get(
                "success",
                False
            )
            else "FAILED"
        )

        log(
            f"[{status}] "
            f"{item.get('input', '')}"
        )

        log(
            f"      → "
            f"{item.get('output', '')}"
        )

        if item.get(
            "error"
        ):

            log(
                f"      ERROR: "
                f"{item['error']}"
            )

    if failed:

        sg.popup(

            "Scanning finished with errors.\n\n"

            f"Successful: {successful}\n"
            f"Failed: {failed}\n"
            f"Pages: {pages}",

            title="OMR Scanner"
        )

    else:

        sg.popup(

            "Scanning completed successfully!\n\n"

            f"Files: {successful}\n"
            f"Pages: {pages}",

            title="OMR Scanner"
        )


# ============================================================
# GUI
# ============================================================

layout = [

    # ========================================================
    # HEADER
    # ========================================================

    [
        sg.Text(

            "OMR SCANNER",

            font=(
                "Arial",
                25,
                "bold"
            ),

            justification="center",

            expand_x=True
        )
    ],

    [
        sg.Text(

            "Scan images, PDFs or an entire directory",

            font=(
                "Arial",
                11
            ),

            text_color=SECONDARY,

            justification="center",

            expand_x=True
        )
    ],

    [
        sg.HorizontalSeparator()
    ],


    # ========================================================
    # INPUT
    # ========================================================

    [
        sg.Frame(

            "📥 INPUT",

            [

                [
                    sg.Radio(

                        "Single File",

                        "input-mode",

                        default=True,

                        key="-MODE_FILE-",

                        enable_events=True
                    ),

                    sg.Radio(

                        "Directory",

                        "input-mode",

                        key="-MODE_DIR-",

                        enable_events=True
                    ),
                ],

                [
                    sg.Text(
                        "Path",
                        size=(12, 1)
                    ),

                    sg.Input(

                        str(
                            DEFAULT_INPUT
                        ),

                        key="-INPUT-",

                        expand_x=True,

                        enable_events=True
                    ),

                    sg.Button(

                        "Browse",

                        key="-BROWSE_INPUT-",

                        size=(10, 1)
                    )
                ],

                [
                    sg.Text(
                        "Files",
                        size=(12, 1)
                    ),

                    sg.Text(

                        "Detecting...",

                        key="-INPUT_INFO-",

                        text_color=SECONDARY,

                        expand_x=True
                    )
                ]
            ],

            expand_x=True
        )
    ],


    # ========================================================
    # TEMPLATE
    # ========================================================

    [
        sg.Frame(

            "📐 TEMPLATE",

            [

                [
                    sg.Text(
                        "Folder",
                        size=(12, 1)
                    ),

                    sg.Input(

                        str(
                            DEFAULT_TEMPLATES
                        ),

                        key="-TEMPLATES-",

                        expand_x=True
                    ),

                    sg.Button(

                        "Browse",

                        key="-BROWSE_TEMPLATES-",

                        size=(10, 1)
                    )
                ],

                [
                    sg.Text(
                        "Force ID",
                        size=(12, 1)
                    ),

                    sg.Input(

                        "",

                        key="-TEMPLATE_ID-",

                        expand_x=True
                    )
                ],

                [
                    sg.Text(
                        "Mode",
                        size=(12, 1)
                    ),

                    sg.Text(

                        "QR template → local template → embedded QR",

                        text_color=SECONDARY,

                        expand_x=True
                    )
                ]
            ],

            expand_x=True
        )
    ],


    # ========================================================
    # OUTPUT
    # ========================================================

    [
        sg.Frame(

            "📤 OUTPUT",

            [

                [
                    sg.Text(
                        "JSON",
                        size=(12, 1)
                    ),

                    sg.Input(

                        str(
                            DEFAULT_JSON_OUTPUT
                        ),

                        key="-JSON-OUTPUT-",

                        expand_x=True
                    ),

                    sg.Button(

                        "Browse",

                        key="-BROWSE_JSON-",

                        size=(10, 1)
                    )
                ],

                [
                    sg.Text(
                        "Debug",
                        size=(12, 1)
                    ),

                    sg.Input(

                        str(
                            DEFAULT_DEBUG_OUTPUT
                        ),

                        key="-DEBUG-OUTPUT-",

                        expand_x=True
                    ),

                    sg.Button(

                        "Browse",

                        key="-BROWSE_DEBUG-",

                        size=(10, 1)
                    )
                ],

                [
                    sg.Checkbox(

                        "Generate debug images",

                        default=True,

                        key="-DEBUG_ENABLED-"
                    )
                ]
            ],

            expand_x=True
        )
    ],


    # ========================================================
    # SCAN CONTROL
    # ========================================================

    [
        sg.Frame(

            "🔍 SCAN",

            [

                [
                    sg.Button(

                        "SCAN",

                        key="-SCAN-",

                        size=(15, 2),

                        font=(
                            "Arial",
                            14,
                            "bold"
                        ),

                        button_color=(
                            FG,
                            "#303030"
                        )
                    )
                ],

                [
                    sg.ProgressBar(

                        100,

                        orientation="h",

                        size=(70, 20),

                        key="-PROGRESS-",

                        expand_x=True
                    )
                ],

                [
                    sg.Text(

                        "Ready",

                        key="-STATUS-",

                        text_color=SUCCESS,

                        justification="center",

                        expand_x=True
                    )
                ]
            ],

            expand_x=True,

            element_justification="center"
        )
    ],


    # ========================================================
    # LOG
    # ========================================================

    [
        sg.Frame(

            "📋 LOG",

            [

                [
                    sg.Multiline(

                        "",

                        key="-LOG-",

                        size=(100, 18),

                        expand_x=True,

                        expand_y=True,

                        autoscroll=True,

                        background_color=PANEL,

                        text_color=FG,

                        disabled=True,

                        write_only=False
                    )
                ]
            ],

            expand_x=True,

            expand_y=True
        )
    ],


    # ========================================================
    # FIXED BOTTOM BUTTON BAR
    # ========================================================

    [
        sg.Button(
            "Clear Log",
            key="-CLEAR-",
            size=(14, 2)
        ),

        sg.Button(
            "Open JSON",
            key="-OPEN_JSON-",
            size=(14, 2)
        ),

        sg.Button(
            "Open Debug",
            key="-OPEN_DEBUG-",
            size=(14, 2)
        ),

        sg.Push(),

        sg.Button(
            "Exit",
            key="-EXIT-",
            size=(12, 2)
        )
    ]
]


# ============================================================
# CREATE WINDOW
# ============================================================

window = sg.Window(

    "OMR Scanner",

    layout,

    size=(
        1100,
        1050
    ),

    resizable=False,

    finalize=True
)


# ============================================================
# INITIAL INFO
# ============================================================

update_input_info(
    DEFAULT_INPUT
)


# ============================================================
# RUN
# ============================================================

while True:

    event, values = window.read()

    # ========================================================
    # EXIT
    # ========================================================

    if event in (
        sg.WIN_CLOSED,
        "-EXIT-"
    ):

        break

    # ========================================================
    # INPUT MODE
    # ========================================================

    if event in (
        "-MODE_FILE-",
        "-MODE_DIR-"
    ):

        directory_mode = (
            values.get(
                "-MODE_DIR-",
                False
            )
        )

        current = values.get(
            "-INPUT-",
            ""
        )

        current_path = Path(
            current
        )

        if directory_mode:

            if current_path.is_file():

                current = str(
                    current_path.parent
                )

                window[
                    "-INPUT-"
                ].update(
                    current
                )

                update_input_info(
                    current
                )

        else:

            if current_path.is_dir():

                window[
                    "-INPUT_INFO-"
                ].update(

                    "Select a single image/PDF.",

                    text_color=WARNING
                )

    # ========================================================
    # BROWSE INPUT
    # ========================================================

    if event == "-BROWSE_INPUT-":

        browse_input(

            values.get(
                "-MODE_DIR-",
                False
            )
        )

    # ========================================================
    # INPUT CHANGED
    # ========================================================

    if event == "-INPUT-":

        update_input_info(
            values.get(
                "-INPUT-",
                ""
            )
        )

    # ========================================================
    # BROWSE TEMPLATES
    # ========================================================

    if event == "-BROWSE_TEMPLATES-":

        browse_folder(

            "-TEMPLATES-",

            "Select Templates directory",

            DEFAULT_TEMPLATES
        )

    # ========================================================
    # BROWSE JSON
    # ========================================================

    if event == "-BROWSE_JSON-":

        browse_folder(

            "-JSON-OUTPUT-",

            "Select JSON output directory",

            DEFAULT_JSON_OUTPUT
        )

    # ========================================================
    # BROWSE DEBUG
    # ========================================================

    if event == "-BROWSE_DEBUG-":

        browse_folder(

            "-DEBUG-OUTPUT-",

            "Select debug output directory",

            DEFAULT_DEBUG_OUTPUT
        )

    # ========================================================
    # SCAN
    # ========================================================

    if event == "-SCAN-":

        start_scan(
            values
        )

    # ========================================================
    # STATUS FROM WORKER
    # ========================================================

    if event == "-STATUS_EVENT-":

        message = (
            values[
                "-STATUS_EVENT-"
            ]
        )

        window[
            "-STATUS-"
        ].update(

            message.get(
                "text",
                "Scanning..."
            ),

            text_color=WARNING
        )

    # ========================================================
    # SCAN FINISHED
    # ========================================================

    if event == "-SCAN_FINISHED-":

        results = (
            values[
                "-SCAN_FINISHED-"
            ]
        )

        handle_finished(
            results
        )

    # ========================================================
    # SCAN FAILED
    # ========================================================

    if event == "-SCAN_FAILED-":

        error = (
            values[
                "-SCAN_FAILED-"
            ]
        )

        set_running(
            False
        )

        window[
            "-STATUS-"
        ].update(

            "Scan failed",

            text_color=ERROR
        )

        log(
            ""
        )

        log(
            "ERROR:"
        )

        log(
            error
        )

        sg.popup_error(

            "Scanner failed:\n\n"
            f"{error}",

            title="OMR Scanner"
        )

    # ========================================================
    # CLEAR
    # ========================================================

    if event == "-CLEAR-":

        window[
            "-LOG-"
        ].update(
            ""
        )

    # ========================================================
    # OPEN JSON
    # ========================================================

    if event == "-OPEN_JSON-":

        path = Path(
            values.get(
                "-JSON-OUTPUT-",
                DEFAULT_JSON_OUTPUT
            )
        )

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        os.system(
            f'xdg-open "{path}"'
        )

    # ========================================================
    # OPEN DEBUG
    # ========================================================

    if event == "-OPEN_DEBUG-":

        path = Path(
            values.get(
                "-DEBUG-OUTPUT-",
                DEFAULT_DEBUG_OUTPUT
            )
        )

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        os.system(
            f'xdg-open "{path}"'
        )


# ============================================================
# CLOSE
# ============================================================

window.close()