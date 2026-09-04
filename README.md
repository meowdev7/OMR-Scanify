# OMR-Scanify

OMR-Scanify is a school project developed by a group of XII graders to automate OMR sheet scanning, answer evaluation, and report generation.

## 👥 Team & Roles

*   **Achintya Srivastava** (@meowdev7) [XII A1] — Project Lead, Backend (Go)
*   **Aryan Kushwaha** (@theprogrammer001) [XII B1] — OMR Scanning & Sheet Generation (Python / OpenCV)
*   **Kushagra Sharma** (@flinshnezh) [XII B1] — Desktop GUI Interface (Python / Tkinter)
*   **Raj Tandon** (@darklord1904-og) [XII A1] — Quality Assurance, Testing & GUI Support

---

## 🏗️ Architecture & Data Flow

 
Architecture
1.  **Python / OpenCV:** Processes the OMR image, detects bubbles, extracts answers, and sends a normalized submission to the backend. Empty or ambiguous bubbles are sent as unattempted answers.
2.  **Go Backend:** Manages project state, runs evaluation logic against an answer key, manages student records in-memory, and handles CSV exports.
3.  **Tkinter Frontend:** Provides a desktop dashboard for teachers to create tests, manage answer keys, upload sheets, and view analysis results.

### Scan and Evaluation Workflow

1. Create a project and set its question count.
2. Create or upload an answer key. The key must contain exactly one `A`, `B`, `C`, or `D` answer for each question.
3. Generate the QR-coded OMR packet from the project generator and print every page at its original scale. The packet contains one student-details page followed by one or more answer pages.
4. Fill the student-detail bubbles and answer bubbles clearly, then upload all packet pages together from the project action/details page.
5. The scanner groups pages by QR sheet ID, reads the identity page, reads answers from answer pages, and sends one combined submission to the backend.
6. The backend compares each answer with the key and stores the result. Open Analysis to review the large `Score`, `Correct`, `Incorrect`, and `Unattempted` summary cards and the question-level table.

Generated A4 portrait packets now use a separate CBSE-style identity page with
character bubbles for candidate name and subject, eight roll-number digit
columns, and choice bubbles for class, section, and set code. The QR remains
the primary identity reference; the scanner compares bubbled name, class,
section, and roll number with the QR details and records `verified` or
`mismatch` status. Answer pages contain only the question bubbles.

`Score` is the number of correct answers, shown as `correct/total_questions`. Incorrect and unattempted answers do not add marks. A blank or ambiguous scan is represented as `null` and evaluated as `Unattempted`.

If a sheet was uploaded before a scanner correction or after changing the answer key, upload it again. Results already stored by the backend are not rescanned automatically.

---

## ⚙️ Backend Specifications (Go)

The backend is built strictly using the **Go Standard Library** (no external dependencies) to keep it lightweight and portable. 

*   **Base URL:** `http://localhost:8080`
*   **Data Persistence:** In-memory storage (optimized for live demo presentation).

### 🚀 API Endpoints

#### 1. Projects Management
*   **`POST /api/v1/projects`** — Create a new examination project.
    *   *Request Body:* `{ "name": "Physics Unit Test 1", "question_count": 8 }`
    *   *Response:* `21 Created` with project object details and an assigned `{id}`.
*   **`GET /api/v1/projects`** — List all created projects.
*   **`GET /api/v1/projects/{id}`** — Fetch a single project configuration.

#### 2. Configuration & Student Setup
*   **`PUT /api/v1/projects/{id}/answer-key`** — Save the official grading key.
    *   *Request Body:* `{ "answer_key": ["A", "B", "C", "D", "A", "B", "C", "D"] }` *(Array length must exactly match `question_count`)*
*   **`POST /api/v1/projects/{id}/students/import`** — Bulk import students via raw CSV body data.
    *   *Required Headers:* `id,name,class,section,roll_no`
    *   *Note:* Automatically generates a deterministic sheet string ID (e.g., `PROJECTID-S0001`).

#### 3. Evaluation & Results
*   **`POST /api/v1/projects/{id}/submissions`** — Process scanned OMR metrics.
    *   *Request Body:*
        ```json
        {
          "sheet_id": "PHY-001-S0001",
          "answers": ["A", "C", "B", null, "D", "A", "B", "C"]
        }
        ```
    *   *Response Body (Evaluated Scorecard):*
        ```json
        {
          "sheet_id": "PHY-001-S0001",
          "student_id": "STU-001",
          "student_name": "Example Student",
          "correct": 3,
          "incorrect": 4,
          "unattempted": 1,
          "marks": 3,
          "total_questions": 8
        }
        ```
*   **`GET /api/v1/projects/{id}/results`** — Fetch list of all evaluated student summaries.
*   **`GET /api/v1/projects/{id}/results/export`** — Stream download a compiled CSV spreadsheet report.
    *   *Output Columns:* `sheet_id,student_id,student_name,correct,incorrect,unattempted,marks,total_questions`

---

## 💻 Development & Execution

### Prerequisites
Ensure you have **Go 1.16+** installed on your system.

### Running the Server
From the root of the `/backend` directory, spin up the development environment:
```bash
go run ./
```
The server binds and listens on port `:8080`.

### Executing Tests
To verify logic stability and route evaluation engines, run:
```bash
go test -v ./...
```

### Scanner Development Check

The scanner is implemented in `services/Scanner/OMR_scanner.py`. Bubble scores
are measured inside each bubble and compared with local thresholds so printed
outlines are not mistaken for filled answers. When changing scanner behavior,
validate both an empty sheet and a sheet with known filled bubbles before using
the frontend workflow.
