# OMR Scanify Frontend

The `frontend` directory contains the Tkinter desktop interface for OMR Scanify. It provides the dashboard, project navigation, project creation dialog, project listing, project actions, and an embedded OMR generator. The frontend communicates with the Go backend over HTTP for project creation and management, and integrates with the Python services layer for OMR generation and scanning capabilities.

## Overview

The frontend is a cross-platform desktop application built with Tkinter that enables users to:
- Create and manage OMR projects
- Configure project settings and answer keys
- Generate OMR sheets with customizable layouts
- Preview generated sheets in real-time
- Export sheets as PDF
- Manage students and submissions
- View and analyze scanning results

## Recent Changes & Improvements

### Latest Enhancements
- **Project Action Page**: Added post-creation workflow page showing success confirmation and next-step options for users
- **Real-time Preview System**: Implemented debounced preview updates in the OMR generator to reduce backend load while maintaining responsive UI
- **Backend Integration**: Full integration with the Go backend API for project lifecycle management
- **Enhanced Project Management**: Project deletion and renaming capabilities in the projects list view
- **API-Driven Data Flow**: All project data flows through the REST API, ensuring consistency across components
- **Sidebar Navigation**: Added dedicated navigation sidebar for Dashboard, Projects, OMR Generator, and bottom-positioned Settings views
- **Theme Settings**: Added Dark, Light, and System appearance modes with immediate UI updates
- **Centralized Theme Application**: Shared palette and widget styling logic keeps the interface consistent across pages and dialogs

## Features

- **Dashboard**: Landing page with quick action for creating a new OMR project.
- **Projects View**: Display all projects with cards showing project name, question count, student count, and result count.
- **Project Management**: Search, sort, delete, and rename projects (implemented via API).
- **Empty-State UI**: Illustration and create-project action shown when no projects exist.
- **Project Creation Dialog**: Modal form for creating new projects with name and question count validation.
- **Project Action Page**: Post-creation workflow showing success message and next actions (answer key setup, sheet generation).
- **Embedded OMR Generator**: Built-in OMR sheet generator using the engine from `services/Generators/OMR_generator.py`.
  - Configurable page size (A4, Letter, etc.)
  - Configurable orientation (Portrait, Landscape)
  - Customizable number of questions and options per question
  - Student detail fields (name, class, section, admission number, subject)
  - QR code embedding for sheet tracking
- **Real-time Preview System**: Debounced preview updates when generator settings or student details change, reducing server load.
- **PDF Export**: Generate and download OMR sheets as PDF from the frontend.
- **Project-Aware Generator**: OMR generator page maintains state per project and can be refreshed with project updates.
- **Cross-Platform Asset Resolution**: Image assets resolved relative to the frontend source directory, works across Windows, Linux, and macOS.
- **Theme Selection**: Choose Dark, Light, or System mode from Settings. The selected mode is applied immediately to the main window, sidebar, pages, dialogs, and controls.
- **Dark and Light Palettes**: Centralized window, sidebar, panel, border, text, muted, accent, and hover colors are defined in `theme.py`.
- **System Theme Detection**: System mode reads the Windows application theme preference and falls back to Dark when it cannot be detected.
- **Hover Feedback**: Action buttons show the blue accent only while the pointer is over them and restore their surrounding background when the pointer leaves.
- **Project Deletion & Renaming**: Right-click context menu on project cards for management actions.

## API Documentation

The frontend communicates with the Go backend via REST API at `http://127.0.0.1:8080/api/v1`. All API calls are handled in `storage.py` and `functions.py`.

### Project Endpoints

#### Create Project
```
POST /api/v1/projects
Content-Type: application/json

Request Body:
{
  "name": "Physics Midterm",
  "question_count": 50
}

Response (201):
{
  "id": "proj-12345",
  "name": "Physics Midterm",
  "question_count": 50,
  "created_at": "2025-08-23T10:30:00Z",
  "student_count": 0,
  "result_count": 0
}
```
**Frontend Usage**: `functions.py:create_project()` - Called when user submits the Create Project dialog.

#### Get All Projects
```
GET /api/v1/projects

Response (200):
[
  {
    "id": "proj-12345",
    "name": "Physics Midterm",
    "question_count": 50,
    "created_at": "2025-08-23T10:30:00Z",
    "student_count": 0,
    "result_count": 0
  },
  ...
]
```
**Frontend Usage**: `storage.py:load_projects()` - Called when displaying the Projects page to populate project cards.

#### Get Single Project
```
GET /api/v1/projects/{id}

Response (200):
{
  "id": "proj-12345",
  "name": "Physics Midterm",
  "question_count": 50,
  "created_at": "2025-08-23T10:30:00Z",
  "student_count": 5,
  "result_count": 3,
  "answer_key": [1, 2, 3, 4, 1, ...],
  "students": [
    {"id": "student-1", "name": "John Doe", ...}
  ]
}
```
**Frontend Usage**: `storage.py:get_project()` - Called when opening a project's details or in the OMR generator.

### Student Management

#### Import Students from CSV
```
POST /api/v1/projects/{id}/students/import
Content-Type: text/csv

Request Body (CSV format):
name,class,section,admission
John Doe,10,A,1001
Jane Smith,10,B,1002

Response (200):
{
  "imported": 2,
  "project_id": "proj-12345"
}
```
**Frontend Usage**: `storage.py:import_students()` - Retained for compatibility; normal scanning retrieves student details from the sheet QR code.

### Answer Key Management

Answer keys are uploaded from the project action/details page as CSV files. The supported format is one answer per row in question order, for example:

```csv
A
B
C
D
```

The optional two-column format `question,answer` is also supported. Answers are trimmed, case-normalized, and must be `A`, `B`, `C`, or `D`; the number of answers must match the project's `question_count`. The key is stored in the owning project JSON file and is displayed when its saved project card is opened.

#### Set Answer Key
```
PUT /api/v1/projects/{id}/answer-key
Content-Type: application/json

Request Body:
{
  "answer_key": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]
}

Response (200):
{
  "id": "proj-12345",
  "answer_key": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]
}
```
**Frontend Usage**: `storage.py:update_answer_key()` - Called from project action page when user sets the answer key.

### OMR Sheet Generation

#### Generate OMR Sheets
```
POST /api/v1/projects/{id}/sheets/generate
Content-Type: application/json

Request Body:
{
  "page_size": "A4",
  "orientation": "Portrait",
  "questions": 50,
  "options": 4,
  "student_name": "John Doe",
  "class_standard": "10",
  "section": "A",
  "admission": "1001",
  "subject": "Physics",
  "qr_enabled": true
}

Response (200):
{
  "sheets": ["base64_encoded_image_1", "base64_encoded_image_2"],
  "page_count": 2
}
```
**Frontend Usage**: `omr_generator.py` - Called when user clicks "Generate Preview" or "Export PDF" in the generator page. Images are decoded and displayed in real-time.

### Results Endpoints

#### Get Project Results
```
GET /api/v1/projects/{id}/results

Response (200):
{
  "results": [
    {
      "student_id": "student-1",
      "student_name": "John Doe",
      "score": 45,
      "total": 50,
      "percentage": 90.0
    },
    ...
  ]
}
```

#### Get Student Result
```
GET /api/v1/projects/{id}/results/{student_id}

Response (200):
{
  "student_id": "student-1",
  "student_name": "John Doe",
  "answers": [1, 2, 3, 4, 1, ...],
  "correct_answers": [1, 2, 3, 4, 1, ...],
  "score": 45,
  "total": 50,
  "percentage": 90.0
}
```

#### Export Results as CSV
```
GET /api/v1/projects/{id}/results/export

Response (200): CSV file download
student_name,score,total,percentage
John Doe,45,50,90.0
Jane Smith,48,50,96.0
```

### Submission Endpoints

#### Submit OMR Sheet for Evaluation
```
POST /api/v1/projects/{id}/submissions
Content-Type: application/json

Request body:
{
  "sheet_id": "project-S0001",
  "answers": ["A", null, "C", "D"]
}

Response (200):
{
  "sheet_id": "project-S0001",
  "student_id": "student-1",
  "student_name": "John Doe",
  "correct": 3,
  "incorrect": 0,
  "unattempted": 1,
  "marks": 3,
  "total_questions": 4
}
```

PNG, JPG, and JPEG answer sheets are uploaded through `Upload Answer Sheets`.
The scanner reads each QR-coded sheet, sends the embedded student details and
answers to the backend, and the backend evaluates and stores the result. The
student is added to the project automatically; a roster CSV is not required.
Multiple image files can be selected at once. After processing, the Analysis
window shows the batch summary, failed files, and question-level results. Saved
results can be reopened later from the project analysis action.

## Directory Contents

| File | Purpose |
| --- | --- |
| `UI.py` | Application entry point. Creates the main window (1280x720), manages the sidebar, dashboard, projects page, and project action pages. Handles navigation between views and coordinates callbacks from child pages. |
| `projects.py` | Builds the Projects page with project cards. Loads all projects via API, renders cards with project details, handles project refresh, and provides context menu actions (delete, rename). Displays empty-state UI when no projects exist. |
| `functions.py` | Handles project creation workflow. Creates and manages the project creation dialog (modal window), validates user input, sends project data to backend, shows success/error messages, and invokes the callback on successful creation. |
| `project_action.py` | Builds the project action/workflow page shown after successful project creation. Displays success message and provides quick-action buttons to import students, upload and analyze answer sheets, set an answer key, or generate OMR sheets. |
| `omr_generator.py` | Builds the embedded OMR Generator page with live preview. Manages generator state (page size, orientation, questions, options, student details, QR settings). Handles real-time preview generation with debouncing, PDF export, and project context awareness. |
| `sidebar.py` | Builds the left-side navigation sidebar with OMR Scanify branding and navigation buttons. Settings is packed at the bottom of the sidebar; OMR generation is accessed from a selected project. |
| `settings.py` | Builds the Settings page. Provides Dark, Light, and System appearance choices, updates the selected state, and requests an application-wide theme refresh. |
| `theme.py` | Defines Dark and Light palettes, detects the Windows system theme, resolves the selected mode, translates legacy widget colors, and applies colors and hover behavior recursively to the interface. |
| `storage.py` | API communication layer for all backend interactions. Encapsulates all HTTP requests to the Go backend for projects, students, answer keys, and results. Handles configuration directory resolution using `platformdirs`. |
| `assets.py` | Resolves image asset paths relative to the Python module location using `Path(__file__).resolve()`. Ensures cross-platform asset loading (Windows, Linux, macOS) independent of working directory. |
| `omricon.png` | Application window icon (appears in taskbar and window title bar). |
| `foldericon.png` | Icon displayed on the "Create Project" dashboard card. |
| `empty_project_img.png` | Illustration shown in the Projects page when no projects exist, encouraging users to create their first project. |

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
- **Settings** calls `show_settings()` and is anchored to the bottom of the sidebar.
- Hover handlers change the background color of each navigation button.

### Settings and Themes

The Settings page is created by `create_settings_page()` in `settings.py`. Its Appearance section provides three modes:

- **Dark**: Uses the dark application palette.
- **Light**: Uses the light application palette.
- **System**: Detects the operating system theme. On Windows, this reads `AppsUseLightTheme` from the user theme settings.

Selecting a mode immediately updates the main window, sidebar, dashboard, project pages, generator, settings page, and dialogs through `apply_theme()` in `theme.py`. Action buttons use the blue accent while hovered and return to the background of their surrounding container when the pointer leaves.

The selected mode is stored by the Go backend in the user's OMR Scanify configuration directory and restored when `UI.py` starts. If the backend is unavailable, the frontend falls back to Dark for that session.

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

The project action page is built by `create_project_action_window()` in `project_action.py`. It is an embedded frame, not a separate movable window, so it stays inside the main content area beside the sidebar. It provides navigation back to Projects, displays the project's saved answer key, supports CSV upload/replacement, and provides a Create OMR action.

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

## Architecture & Design

### Component Structure

The frontend follows a modular, page-based architecture where each major UI section is independently created and managed:

```
UI.py (Main Application)
├── sidebar.py (Navigation)
├── Dashboard (Direct in UI.py)
├── projects.py (Projects Page)
├── project_action.py (Post-Creation Workflow)
└── omr_generator.py (Generator Interface)

storage.py (API Layer)
└── All HTTP communication to Go backend

assets.py (Asset Resolution)
└── Cross-platform image loading

functions.py (Project Creation Dialog)
└── Modal form for new projects
```

### Data Flow

**Creating a Project:**
```
User clicks "Create" → functions.py opens dialog → User submits form → 
create_project() sends POST to /api/v1/projects → Backend creates project →
on_project_created() callback fires → projects_page.refresh_projects() →
show_project_actions(project) displays workflow page
```

**Loading Projects:**
```
Application startup or refresh → storage.py:load_projects() → 
GET /api/v1/projects → projects.py creates project cards from response →
Cards display name, question_count, student_count, result_count
```

**Generating OMR Sheets:**
```
User enters generator settings → debounced preview update → 
omr_generator.py sends POST to /api/v1/projects/{id}/sheets/generate →
Backend generates sheet images as base64 → Frontend decodes and displays preview →
User clicks "Export PDF" → omr_generator.py generates PDF locally and opens download dialog
```

**Managing Answer Keys:**
```
User enters answer key in project action page → storage.py:update_answer_key() →
PUT /api/v1/projects/{id}/answer-key → Backend persists answer key →
Frontend shows confirmation message
```

### Page Navigation

Pages are managed as Tkinter frames that are packed/unpacked dynamically:

```python
# Show a page
page_frame.pack(side="left", fill="both", expand=True)

# Hide a page
page_frame.pack_forget()
```

The `show_dashboard()`, `show_projects()`, and `show_generator()` functions in `UI.py` coordinate this navigation. Only one page is visible at a time alongside the sidebar.

### State Management

State is primarily managed through:
- **Project Object**: Passed between pages via function parameters
- **Dictionary Caching**: `omr_generator.py` maintains generator state in Tkinter `StringVar`/`BooleanVar` objects
- **Global Variables**: `UI.py` maintains `current_project` and page references as globals
- **Theme State**: `UI.py` maintains the selected `theme_mode` for the active session and passes it to pages and dialogs through the window theme state
- **API Responses**: Backend project data is the source of truth; frontend caches it locally

Debouncing is implemented in `omr_generator.py` to batch rapid preview updates and reduce backend load:
```python
preview_job = {"value": None}  # Stores scheduled preview update
# Subsequent changes cancel the previous job and schedule a new one
```

## Configuration

### Backend Connection

The backend URL is configured in `storage.py`:

```python
API_URL = "http://127.0.0.1:8080/api/v1"
```

To connect to a different backend:
1. Edit `storage.py` and update `API_URL`
2. Ensure the backend is running and listening on the configured host/port
3. Restart the frontend

### Project Storage Directory

The project storage directory is automatically resolved via `platformdirs`:

```python
config_dir = Path(platformdirs.user_config_dir(roaming=True))
projects_dir = config_dir / APP_NAME / "projects"
```

On **Windows**: `%APPDATA%\OMR-Scanify\projects`
On **Linux**: `~/.config/omr-scanify/projects` (or `$XDG_CONFIG_HOME/...` if set)
On **macOS**: `~/Library/Application Support/OMR-Scanify/projects`

### Theme Configuration

Theme palettes and theme application behavior are defined in `theme.py`:

```python
PALETTES = {
  "dark": {...},
  "light": {...},
}
```

The initial frontend mode is set in `UI.py` with `theme_mode = "dark"`. Change the default there only if a different startup mode is required. The `system` mode is resolved at runtime and does not modify the operating system theme.

### Font Configuration

The OMR generator uses platform-specific fonts:
- **Windows**: Segoe UI (primary), Arial (fallback)
- **Linux/macOS**: System fonts as available

Fonts are set in `services/Generators/OMR_generator.py`. Modify if using custom fonts.

### Timeout Configuration

API calls have a default 5-second timeout:

```python
response = requests.get(..., timeout=5)
```

To adjust, edit the `timeout` parameter in `storage.py` or `functions.py`.

## Troubleshooting

### Frontend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'tkinter'`
- **Solution (Windows)**: Tkinter is normally included. Reinstall Python and ensure "tcl/tk and IDLE" is checked during installation.
- **Solution (Ubuntu/Debian)**: `sudo apt-get install python3-tk`
- **Solution (Fedora)**: `sudo dnf install python3-tkinter`
- **Solution (macOS)**: Use Homebrew or conda with Tk support: `brew install python-tk` or use `conda` distribution.

**Problem**: `ModuleNotFoundError: No module named 'requests'` (or other packages)
- **Solution**: Install dependencies: `python -m pip install requests platformdirs pillow qrcode`

**Problem**: Application window appears but crashes immediately
- **Solution**: Check terminal output for Python exceptions. Ensure backend is running if project creation is enabled.

### Backend Connection Issues

**Problem**: "Failed to connect to 127.0.0.1:8080" or "Connection refused"
- **Solution**: Ensure the Go backend is running: `cd backend && go run .`
- **Solution**: Check that the backend is listening on port 8080 (it prints on startup)
- **Solution**: If running on a different machine, edit `API_URL` in `storage.py` to point to the correct host/port

**Problem**: Project creation succeeds but projects don't appear in the list
- **Solution**: Click "Refresh" or restart the frontend
- **Solution**: Check the backend console for errors
- **Solution**: Verify the project JSON file was created in the projects directory

### OMR Generator Issues

**Problem**: Preview shows error or doesn't update
- **Solution**: Check that project question count is set correctly
- **Solution**: Ensure the backend is running for sheet generation
- **Solution**: Try adjusting the page size or orientation
- **Solution**: Check terminal for generator exceptions

**Problem**: PDF export fails or produces blank file
- **Solution**: Ensure Pillow is installed: `python -m pip install pillow`
- **Solution**: Try reducing the page size or number of questions
- **Solution**: Check that the Downloads directory is writable

**Problem**: QR code not generating
- **Solution**: Ensure `qrcode` package is installed: `python -m pip install qrcode`
- **Solution**: Check that QR code is enabled in the generator settings
- **Solution**: Verify that the student name or admission number is filled in

### UI/Display Issues

**Problem**: Text is cut off or overlapping
- **Solution**: Tkinter text rendering depends on available fonts. Ensure Segoe UI (Windows) or standard fonts (Linux/macOS) are installed.
- **Solution**: Try resizing the main window or maximizing it
- **Solution**: On Linux, install fonts: `sudo apt-get install fonts-dejavu fonts-liberation`

**Problem**: Images/icons not loading (show as empty)
- **Solution**: Verify that `.png` files exist in the `frontend/` directory
- **Solution**: Check that you're not running the frontend from a different directory (assets are relative to module location)
- **Solution**: On Linux, ensure PIL/Pillow can render PNG: `sudo apt-get install libpng-dev`

**Problem**: Theme colors look wrong or inverted
- **Solution**: Open Settings and select Dark or Light to compare the two palettes.
- **Solution**: For System mode on Windows, verify the Windows application theme preference.
- **Solution**: Edit the centralized palette values in `theme.py` if custom colors are required.

**Problem**: The selected theme resets after restarting the frontend
- **Solution**: This is currently expected. Theme selection is stored in memory only and is not persisted by the frontend or backend.

### API & Network Issues

**Problem**: Requests timeout frequently
- **Solution**: Increase timeout in `storage.py` or `functions.py` (change `timeout=5` to a higher value like `10`)
- **Solution**: Check network connection and backend performance
- **Solution**: Reduce preview refresh frequency or increase debounce delay in `omr_generator.py`

**Problem**: 400/422 errors when creating projects
- **Solution**: Ensure project name is not empty and question count is a positive integer
- **Solution**: Check that the project name doesn't contain invalid characters (backend may have validation rules)
- **Solution**: Verify backend API contract matches the request format

**Problem**: 500 errors from backend
- **Solution**: Check backend console for detailed error messages
- **Solution**: Ensure all required backend dependencies are installed
- **Solution**: Verify project storage directory exists and is writable

### Data & Storage Issues

**Problem**: Projects appear and disappear or don't save
- **Solution**: Check that the projects directory is writable: `ls -la ~/.config/omr-scanify/projects` (Linux) or Explorer (Windows)
- **Solution**: Ensure backend and frontend are using the same storage directory
- **Solution**: Check disk space availability

**Problem**: Project JSON files are corrupted
- **Solution**: Backend generates JSON; if corrupted, check backend logic
- **Solution**: Delete the corrupted file and recreate the project
- **Solution**: Consider backing up projects directory before troubleshooting

## Performance Optimization

- **Preview Debouncing**: Adjust the debounce delay in `omr_generator.py` to reduce server load during rapid input changes
- **Project Caching**: Consider caching loaded projects in memory to reduce API calls
- **Image Compression**: Large OMR sheets may cause lag; consider compressing preview images
- **Lazy Loading**: Project cards could be virtualized for large project lists
- **Worker Threads**: Long-running operations (sheet generation, PDF export) could run on worker threads to keep UI responsive

## Future Enhancements

- Full implementation of project search and sort controls
- Real-time sheet scanning integration with camera/scanner hardware
- Student import from CSV files
- Batch OMR sheet generation for multiple students
- Project settings editor (edit project name, question count after creation)
- Results viewer with detailed scoring breakdowns
- Project templates for common use cases
- Persist the selected theme mode between application launches
- Keyboard shortcuts and accessibility improvements
- Progress indicators for long-running operations
