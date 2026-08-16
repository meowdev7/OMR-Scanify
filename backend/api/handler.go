package api

import (
	"backend/evaluator"
	"backend/models"
	"backend/project"
	"backend/utils"
	"encoding/json"
	"fmt"
	"net/http"
)

/*
	POST /api/v1/projects/PHY-001/submissions
              │
              ▼
       projectID = PHY-001
              │
              ▼
       GetProjectByID()
              │
              ▼
         Project found
              │
              ▼
       Decode submission
              │
              ▼
     SheetID = PHY-001-S0001
              │
              ▼
    GetStudentBySheetID()
              │
              ▼
        Student found
*/

func SubmissionHandler(w http.ResponseWriter, r *http.Request) {

	// Get the project ID from the URL path

	projectID := r.PathValue("id")

	p := project.GetProjectByID(projectID)
	if p == nil {
		http.Error(w, "Project not found", http.StatusNotFound)
		return
	}

	// Decode the JSON body into a Submission struct

	var submission models.Submission
	err := json.NewDecoder(r.Body).Decode(&submission)
	if utils.CheckHTTPError(w, err, "Invalid JSON", http.StatusBadRequest) {
		return
	}

	// Get the student by sheet ID from the project

	student := project.GetStudentBySheetID(p, submission.SheetID)
	if student == nil {
		http.Error(w, "Student not found", http.StatusNotFound)
		return
	}

	checkedAnswers := evaluator.CheckAnswers(submission.Answers, p.AnswerKey)

	marks := evaluator.CalculateMarks(checkedAnswers)

	fmt.Println("Project ID: ", projectID)
	fmt.Println("Received submission: ", submission)
	fmt.Println("Sheet ID: ", submission.SheetID)
	fmt.Println("Answers: ", &submission.Answers)
	fmt.Println("Checked Answers: ", checkedAnswers)
	fmt.Println("Marks: ", marks)

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Submission endpoint reached")
}
