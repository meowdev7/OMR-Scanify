# OMR Scanify Frontend

The `frontend` directory contains the Tkinter desktop interface for OMR Scanify. It provides the dashboard, project navigation, project creation dialog, project listing, project actions, and an embedded OMR generator. The frontend communicates with the Go backend over HTTP when project creation is enabled and reads persisted project JSON files from the user configuration directory.

## Features

- Dashboard view with a quick action for creating a new OMR project.
- Projects view showing all locally stored projects.
- Project cards displaying the project name, question count, student count, and result count.
- Project search and sort controls are present in the interface for future behavior.
- Empty-project state with an illustration and create-project action.
- Dynamic project refresh after a successful project creation.
- Project action page shown after project creation.
- Embedded OMR Generator page using the engine from `services/Generators/OMR_generator.py`.
- Realtime, debounced OMR preview updates when generator settings or student details change.
- PDF export from the frontend generator page.
- Project-aware generator page that can be refreshed with `set_project(project)`.
- Cross-platform asset resolution relative to the frontend source directory.
- Dark Tkinter interface with sidebar navigation.

## Directory Contents

| File | Purpose |
| --- | --- |
| `UI.py` | Application entry point. Creates the main window, dashboard, sidebar, and projects page, then starts Tkinter's event loop. |
| `projects.py` | Builds the Projects page, loads project JSON files, renders project cards, and exposes `refresh_projects()`. |
| `functions.py` | Creates the project dialog and sends project creation requests to the backend. |
| `project_action.py` | Builds the embedded project-created action page. |
| `omr_generator.py` | Builds the embedded OMR Generator page, live preview, and PDF export controls. Reuses the service OMR engine. |
| `sidebar.py` | Builds the Dashboard, Projects, and OMR Generator navigation buttons. |
| `storage.py` | Resolves the user project directory and loads project JSON files. |
| `assets.py` | Resolves image assets relative to the location of the Python module. |
| `omricon.png` | Application window icon. |
| `foldericon.png` | Dashboard create-project card icon. |
| `empty_project_img.png` | Illustration shown when no projects exist. |

## Requirements

### Runtime

- Python 3.10 or newer is recommended.
- Tkinter must be installed with Python.
  - Windows: normally included with the standard Python installer.
  - Ubuntu/Debian: install the matching `python3-tk` package.
  - Fedora: install the matching `python3-tkinter` package.
  - macOS: use a Python distribution that includes Tk support.
- The Go backend must be running on port `8080` when backend project creation is enabled.

### Python packages

The frontend imports these third-party packages:

```text
requests
platformdirs
Pillow
qrcode
```

Install them with:

```bash
python -m pip install requests platformdirs pillow qrcode
```

The repository's root `requirements.txt` contains additional scanner and generator dependencies. Install it when working with the complete application:

```bash
python -m pip install -r requirements.txt
```

If `requests` or `platformdirs` are not present in that file, install them separately as shown above.

## Running the Frontend

Start the backend first from the backend directory when using backend project creation:

```bash
cd backend
go run .
```

The backend should report that it is listening on `:8080`.

In a second terminal, start the frontend from the repository root:

```bash
python frontend/UI.py
```

The frontend can also be started from another working directory as long as the script is invoked by its path. Assets are resolved using `Path(__file__).resolve()`, so the current working directory does not need to be the repository root.

## Main Window

`UI.py` creates the main application window with a fixed initial size of `1280x720`.

### Sidebar

The sidebar is created by `create_sidebar()` in `sidebar.py`.

- **Dashboard** calls `show_dashboard()` and displays the dashboard frame.
- **Projects** calls `show_projects()` and displays the projects page.
- **OMR Generator** calls `show_generator()` and displays the embedded generator page.
- Hover handlers change the background color of each navigation button.

### Dashboard

The dashboard is built directly in `UI.py` and contains:

- A `Dashboard` heading.
- A subtitle describing project management.
- A `Project` section heading.
- A clickable `Create a New Project` card.
- The folder icon, title, and explanatory subtitle within that card.

The card and each of its child labels bind to the same click handler, `start_scan()`. Despite the current function name, this action opens the project creation dialog. Actual scan-file or camera behavior is marked as future work in `UI.py`.

### Projects Page

The Projects page is built by `create_projects_page()` in `projects.py` and contains:

- A page heading and subtitle.
- A `New Project` button.
- A search field.
- A sort button labeled `Sort by: Recent`.
- Grid and list-style toolbar buttons.
- A `Your Projects` section.
- A project list area.
- An informational footer.

The search, sort, grid, and list controls are currently visual controls. Their behavior has not yet been implemented.

### Project Actions

The project action page is built by `create_project_action_window()` in `project_action.py`. It is an embedded frame, not a separate movable window, so it stays inside the main content area beside the sidebar. It provides navigation back to Projects and a Create OMR action.

### OMR Generator

The generator page is built by `create_omr_generator_page()` in `omr_generator.py`. It is also an embedded frame and reuses `OMRGenerator` from `services/Generators/OMR_generator.py` rather than the service PySimpleGUI form.

The page provides:

- Page size and orientation selection.
- Question count and number of choices.
- Student name, class, section, admission number, and subject fields.
- QR code enable/disable control.
- Live preview of the first generated OMR page.
- PDF export using the existing generator engine.

All controls are connected to a debounced preview refresh. Text changes regenerate after a short pause, while selection and checkbox changes also trigger the preview. The page exposes `set_project(project)` so the same frame can be reused with a different project:

```python
generator_page.set_project(project)
```

`show_generator(project=None)` in `UI.py` updates the active project and displays the generator page. This provides the integration point for passing a project returned by the Go backend.

## Creating a Project

The create flow is:

### Current Preview Mode

Backend creation is currently temporarily disconnected in `UI.py` so the frontend screens can be edited without a running backend. Clicking the dashboard create-project card opens the project action page with the local preview project `Physics Test` and 50 questions. The sidebar generator also uses the current active preview project.

To restore the backend creation flow, `start_scan()` should call `create_project_window()` and pass a callback that receives the created project, refreshes the Projects page, and calls `show_generator(project)` or opens the project action page.

### Backend Creation Flow

When backend creation is enabled:

1. The user clicks the dashboard card, the Projects page `New Project` button, or the empty-state create button.
2. `start_scan()` calls `create_project_window()`.
3. The dialog collects the project name and question count.
4. `create_project()` converts the question count to an integer.
5. A `POST` request is sent to:

   ```text
   http://127.0.0.1:8080/api/v1/projects
   ```

6. The backend returns the created project and saves it as JSON.
7. The callback refreshes `projects_page` and passes the returned project to the project action or generator page.
8. The dialog closes and the new project appears in the existing Projects page immediately.

The current dialog uses a fixed `400x280` size and cannot be resized.

## Backend Request and Project JSON

The creation request contains:

```json
{
  "name": "Physics Unit Test 1",
  "question_count": 20
}
```

The backend project model uses this persisted structure:

```json
{
  "id": "PHYS-001",
  "name": "Physics Unit Test 1",
  "question_count": 20,
  "answer_key": [],
  "students": [],
  "results": []
}
```

The Projects page currently relies on these fields:

| Field | Expected type | Used by the UI |
| --- | --- | --- |
| `id` | string | Stored project identity; not currently displayed. |
| `name` | string | Project card title. Defaults to `Untitled Project` if absent. |
| `question_count` | integer | Question count displayed on the card. Defaults to `0` if absent. |
| `answer_key` | array | Part of the project contract; not currently displayed. |
| `students` | array | Length is used for the student count. |
| `results` | array | Length is used for the result count. |

Missing `students` or `results` values are treated as empty collections by the UI. Invalid JSON files are skipped by `load_projects()` and reported in the terminal.

## Storage Location

Python uses:

```python
platformdirs.user_config_dir(roaming=True) / "OMR-Scanify" / "projects"
```

On Windows this normally resolves to:

```text
%APPDATA%\OMR-Scanify\projects
```

The Go backend uses `os.UserConfigDir()` and the same application directory name, so both components use the same per-user storage location on Windows, Linux, and macOS according to their platform conventions.

Each project is stored as an individual JSON file. The filename is based on the project ID, for example:

```text
%APPDATA%\OMR-Scanify\projects\PHYS-001.json
```

`storage.py` creates the directory automatically when the frontend loads projects.

## Asset Handling

`assets.py` defines:

```python
ASSETS_DIR = Path(__file__).resolve().parent
```

Use `asset_path()` whenever a Tkinter image is loaded:

```python
from assets import asset_path

image = tk.PhotoImage(file=asset_path("foldericon.png"))
```

Do not use paths such as `frontend/foldericon.png` in new code. Those paths depend on the current working directory and can fail when the application is launched from another directory.

## Refreshing the Project List

`create_projects_page()` attaches the refresh function to the returned frame:

```python
projects_page.refresh_projects()
```

The refresh function:

1. Removes the existing project card widgets.
2. Calls `load_projects()` again.
3. Recreates the cards or empty state from the latest JSON files.

This callback should be called after any operation that creates, edits, imports, or deletes project data.

## Error Behavior

Current behavior includes:

- A non-integer question count raises a `ValueError` during creation.
- HTTP errors are not currently shown in a frontend dialog by the stable implementation.
- Network failures will be raised by `requests` and printed by the Python runtime unless handled by a caller.
- Generator validation errors leave the last valid preview visible while the user is editing an incomplete value.
- QR and generator failures are shown in a preview error dialog.
- Invalid or unreadable project JSON files are skipped and reported by `storage.py`.
- If backend creation is enabled and the backend is not running on port `8080`, project creation will fail.

## Development Notes

- Keep Tkinter widget creation on the main thread.
- Keep HTTP calls short and consider moving long-running requests to a worker thread in the future so the UI does not freeze.
- Prefer `tkinter` imports through `import tkinter as tk` in new modules to make widget ownership clear.
- Preserve the JSON field names used by the Go model and the project cards.
- Pass backend project objects to `show_generator(project)` or `generator_page.set_project(project)` instead of creating duplicate generator frames.
- The OMR engine searches Windows Segoe UI and Arial font paths before Linux font paths so generated student details remain readable on Windows.
- Keep assets inside `frontend/` unless the asset resolver is deliberately extended.
- The `create_project()` helper defined in `UI.py` duplicates functionality in `functions.py` and is currently unused. New project creation logic should remain in `functions.py`.

## Basic Verification

Run Python syntax checks from the repository root:

```bash
python -m py_compile frontend/UI.py frontend/functions.py frontend/projects.py frontend/project_action.py frontend/omr_generator.py frontend/sidebar.py frontend/storage.py frontend/assets.py services/Generators/OMR_generator.py
```

Check that the required packages are available:

```bash
python -c "import requests, platformdirs, PIL, qrcode; print('Frontend dependencies are available')"
```

Run the frontend with:

```bash
python frontend/UI.py
```

The current preview mode can open the UI without the backend. Start the backend at `http://127.0.0.1:8080` when reconnecting project creation or other backend operations.
