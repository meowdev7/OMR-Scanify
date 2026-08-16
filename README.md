# OMR-Scanify

OMR-Scanify is a school project developed by a group of XII graders to automate OMR sheet scanning, answer evaluation, and report generation.

## 👥 Team & Roles

*   **Achintya Srivastava** (@meowdev7) [XII A1] — Project Lead, Backend (Go)
*   **Aryan Kushwaha** (@theprogrammer001) [XII B1] — OMR Scanning & Sheet Generation (Python / OpenCV)
*   **Kushagra Sharma** (@flinshnezh) [XII B1] — Desktop GUI Interface (Python / Tkinter)
*   **Raj Tandon** [XII A1] — Quality Assurance, Testing & GUI Support

---

## 🏗️ Architecture & Data Flow

 
Architecture
1.  **Python / OpenCV:** Processes the OMR image, detects bubbles, extracts answers, and transmits a JSON payload to the backend.
2.  **Go Backend:** Manages project state, runs evaluation logic against an answer key, manages student records in-memory, and handles CSV exports.
3.  **Tkinter Frontend:** Provides a desktop dashboard for teachers to create tests, import students, trigger scans, and view scores.

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