package api

import (
	"backend/evaluator"
	"backend/models"
	"backend/project"
	"backend/storage"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
)

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	if err := json.NewEncoder(w).Encode(payload); err != nil {
		http.Error(w, "Failed to encode JSON response", http.StatusInternalServerError)
	}
}

func writeJSONError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}

func normalizeAnswer(value string) string {
	return strings.TrimSpace(strings.ToUpper(value))
}

func isValidMCQAnswer(value string) bool {
	switch value {
	case "A", "B", "C", "D":
		return true
	default:
		return false
	}
}

// PreferencesHandler handles GET and PUT /api/v1/preferences.
func PreferencesHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		preferences, err := storage.LoadPreferences()
		if err != nil {
			writeJSONError(w, http.StatusInternalServerError, "Failed to load preferences")
			return
		}
		writeJSON(w, http.StatusOK, preferences)
	case http.MethodPut:
		var preferences storage.Preferences
		if err := json.NewDecoder(r.Body).Decode(&preferences); err != nil {
			writeJSONError(w, http.StatusBadRequest, "Invalid JSON")
			return
		}

		if preferences.Theme != "dark" && preferences.Theme != "light" && preferences.Theme != "system" {
			writeJSONError(w, http.StatusBadRequest, "Invalid theme")
			return
		}

		if err := storage.SavePreferences(preferences); err != nil {
			writeJSONError(w, http.StatusInternalServerError, "Failed to save preferences")
			return
		}
		writeJSON(w, http.StatusOK, preferences)
	default:
		writeJSONError(w, http.StatusMethodNotAllowed, "Method not allowed")
	}
}

// SubmissionHandler handles POST /api/v1/projects/{id}/submissions

func SubmissionHandler(w http.ResponseWriter, r *http.Request) {
	projectID := r.PathValue("id")
	if projectID == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	p := project.GetProjectByID(projectID)
	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	var submission models.Submission

	if err := json.NewDecoder(r.Body).Decode(&submission); err != nil {
		writeJSONError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	if submission.SheetID == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing sheet_id")
		return
	}

	student := project.GetStudentBySheetID(p, submission.SheetID)
	if student == nil {
		writeJSONError(w, http.StatusNotFound, "Student not found")
		return
	}

	if len(p.AnswerKey) == 0 {
		writeJSONError(w, http.StatusConflict, "Answer key not set for project")
		return
	}

	if len(submission.Answers) != p.QuestionCount {
		writeJSONError(
			w,
			http.StatusBadRequest,
			"Answer count does not match project question count",
		)
		return
	}

	for i, a := range submission.Answers {
		if a == nil {
			continue
		}

		v := normalizeAnswer(*a)

		if !isValidMCQAnswer(v) {
			writeJSONError(
				w,
				http.StatusBadRequest,
				fmt.Sprintf("Invalid answer at index %d", i),
			)
			return
		}

		*submission.Answers[i] = v
	}

	checkedAnswers := evaluator.CheckAnswers(
		submission.Answers,
		p.AnswerKey,
	)

	marks := evaluator.CalculateMarks(checkedAnswers)

	correct, incorrect, unattempted := 0, 0, 0

	for _, res := range checkedAnswers {
		switch res {
		case "Correct":
			correct++
		case "Incorrect":
			incorrect++
		case "Unattempted":
			unattempted++
		}
	}

	result := models.Result{
		SheetID:        submission.SheetID,
		StudentID:      student.ID,
		StudentName:    student.Name,
		Correct:        correct,
		Incorrect:      incorrect,
		Unattempted:    unattempted,
		Marks:          marks,
		TotalQuestions: p.QuestionCount,
	}

	project.AddResultToProject(p, result)

	if err := storage.SaveProjects(project.Projects); err != nil {
		writeJSONError(
			w,
			http.StatusInternalServerError,
			"Failed to save project",
		)
		return
	}

	writeJSON(w, http.StatusOK, result)
}

// CreateProjectHandler handles POST /api/v1/projects

func CreateProjectHandler(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Name          string `json:"name"`
		QuestionCount int    `json:"question_count"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSONError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	if strings.TrimSpace(req.Name) == "" || req.QuestionCount <= 0 {
		writeJSONError(w, http.StatusBadRequest, "Invalid project data")
		return
	}

	p := project.CreateProject(req.Name, req.QuestionCount)

	if err := storage.SaveProjects(project.Projects); err != nil {
		writeJSONError(
			w,
			http.StatusInternalServerError,
			"Failed to save project",
		)
		return
	}

	fmt.Printf("Created project: %+v\n", p)

	writeJSON(w, http.StatusCreated, p)
}

// ListProjectsHandler handles GET /api/v1/projects

func ListProjectsHandler(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, project.Projects)

	fmt.Printf("Listed projects: %+v\n", project.Projects)
}

// GetProjectHandler handles GET /api/v1/projects/{id}

func GetProjectHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	p := project.GetProjectByID(id)

	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	writeJSON(w, http.StatusOK, p)

	fmt.Printf("Retrieved project: %+v\n", p)
}

// RenameProjectHandler handles PATCH /api/v1/projects/{id}

func RenameProjectHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	var req struct {
		Name          *string `json:"name"`
		QuestionCount *int    `json:"question_count"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSONError(w, http.StatusBadRequest, "Invalid project name")
		return
	}

	if req.Name == nil && req.QuestionCount == nil {
		writeJSONError(w, http.StatusBadRequest, "No project values provided")
		return
	}
	if req.Name != nil && strings.TrimSpace(*req.Name) == "" {
		writeJSONError(w, http.StatusBadRequest, "Invalid project name")
		return
	}
	if req.QuestionCount != nil && *req.QuestionCount <= 0 {
		writeJSONError(w, http.StatusBadRequest, "Question count must be positive")
		return
	}

	p := project.GetProjectByID(id)
	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}
	if req.QuestionCount != nil && *req.QuestionCount != p.QuestionCount && len(p.AnswerKey) > 0 {
		writeJSONError(w, http.StatusConflict, "Remove the existing answer key before changing question count")
		return
	}
	if req.Name != nil {
		p.Name = strings.TrimSpace(*req.Name)
	}
	if req.QuestionCount != nil {
		p.QuestionCount = *req.QuestionCount
	}

	if err := storage.SaveProjects(project.Projects); err != nil {
		writeJSONError(w, http.StatusInternalServerError, "Failed to save project")
		return
	}

	writeJSON(w, http.StatusOK, p)
}

// DeleteProjectHandler handles DELETE /api/v1/projects/{id}

func DeleteProjectHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	deleted := project.DeleteProject(id)
	if deleted == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	if err := storage.DeleteProject(id); err != nil {
		project.Projects = append(project.Projects, *deleted)
		writeJSONError(w, http.StatusInternalServerError, "Failed to delete project")
		return
	}

	writeJSON(w, http.StatusOK, map[string]string{"status": "project deleted"})
}

// UpdateAnswerKeyHandler handles PUT /api/v1/projects/{id}/answer-key

func UpdateAnswerKeyHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	p := project.GetProjectByID(id)

	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	var req struct {
		AnswerKey []string `json:"answer_key"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSONError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	if len(req.AnswerKey) != p.QuestionCount {
		writeJSONError(
			w,
			http.StatusBadRequest,
			"Answer key length must match project question count",
		)
		return
	}

	normalized := make([]string, len(req.AnswerKey))

	for i, answer := range req.AnswerKey {
		if strings.TrimSpace(answer) == "" {
			writeJSONError(
				w,
				http.StatusBadRequest,
				fmt.Sprintf("Invalid answer key at index %d", i),
			)
			return
		}

		v := normalizeAnswer(answer)

		if !isValidMCQAnswer(v) {
			writeJSONError(
				w,
				http.StatusBadRequest,
				fmt.Sprintf("Invalid answer key at index %d", i),
			)
			return
		}

		normalized[i] = v
	}

	p.AnswerKey = normalized

	if err := storage.SaveProjects(project.Projects); err != nil {
		writeJSONError(
			w,
			http.StatusInternalServerError,
			"Failed to save project",
		)
		return
	}

	fmt.Printf(
		"Updated answer key for project %s: %+v\n",
		p.ID,
		p.AnswerKey,
	)

	writeJSON(w, http.StatusOK, map[string]string{
		"status": "answer key updated",
	})
}

// ImportStudentsHandler handles POST /api/v1/projects/{id}/students/import
// CSV body

func ImportStudentsHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	p := project.GetProjectByID(id)

	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	reader := csv.NewReader(r.Body)

	records, err := reader.ReadAll()
	if err != nil && err != io.EOF {
		writeJSONError(w, http.StatusBadRequest, "Invalid CSV")
		return
	}

	if len(records) < 1 {
		writeJSONError(
			w,
			http.StatusBadRequest,
			"CSV missing header or rows",
		)
		return
	}

	header := records[0]

	idxMap := map[string]int{}

	for i, h := range header {
		idxMap[strings.ToLower(strings.TrimSpace(h))] = i
	}

	for _, field := range []string{"id", "name", "roll_no"} {
		if _, ok := idxMap[field]; !ok {
			writeJSONError(
				w,
				http.StatusBadRequest,
				fmt.Sprintf("CSV missing required column: %s", field),
			)
			return
		}
	}

	existingStudents := make(map[string]bool)

	for _, student := range p.Students {
		existingStudents[student.ID] = true
	}

	seenWithinCSV := make(map[string]bool)

	var imported []models.Student

	start := len(p.Students)

	for i := 1; i < len(records); i++ {
		row := records[i]

		if len(row) == 0 {
			continue
		}

		idValue := strings.TrimSpace(row[idxMap["id"]])
		nameValue := strings.TrimSpace(row[idxMap["name"]])
		rollNoValue := strings.TrimSpace(row[idxMap["roll_no"]])

		if idValue == "" || nameValue == "" || rollNoValue == "" {
			writeJSONError(
				w,
				http.StatusBadRequest,
				fmt.Sprintf("Row %d missing required fields", i+1),
			)
			return
		}

		if seenWithinCSV[idValue] || existingStudents[idValue] {
			writeJSONError(
				w,
				http.StatusBadRequest,
				fmt.Sprintf("Duplicate student ID: %s", idValue),
			)
			return
		}

		student := models.Student{
			ID:     idValue,
			Name:   nameValue,
			RollNo: rollNoValue,
		}

		if v, ok := idxMap["class"]; ok && v < len(row) {
			student.Class = strings.TrimSpace(row[v])
		}

		if v, ok := idxMap["section"]; ok && v < len(row) {
			student.Section = strings.TrimSpace(row[v])
		}

		seq := start + len(imported) + 1

		student.SheetID = fmt.Sprintf(
			"%s-S%04d",
			p.ID,
			seq,
		)

		p.Students = append(p.Students, student)
		imported = append(imported, student)

		seenWithinCSV[idValue] = true
		existingStudents[idValue] = true
	}

	if err := storage.SaveProjects(project.Projects); err != nil {
		writeJSONError(
			w,
			http.StatusInternalServerError,
			"Failed to save project",
		)
		return
	}

	fmt.Printf(
		"Imported %d students for project %s\n",
		len(imported),
		p.ID,
	)

	writeJSON(w, http.StatusOK, imported)
}

// ListResultsHandler handles GET /api/v1/projects/{id}/results

func ListResultsHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	p := project.GetProjectByID(id)

	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	writeJSON(w, http.StatusOK, p.Results)

	fmt.Printf(
		"Listed results for project %s: %+v\n",
		p.ID,
		p.Results,
	)
}

// ExportResultsCSVHandler handles
// GET /api/v1/projects/{id}/results/export

func ExportResultsCSVHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	if id == "" {
		writeJSONError(w, http.StatusBadRequest, "Missing project id in path")
		return
	}

	p := project.GetProjectByID(id)

	if p == nil {
		writeJSONError(w, http.StatusNotFound, "Project not found")
		return
	}

	filename := fmt.Sprintf(
		"project-%s-results.csv",
		p.ID,
	)

	w.Header().Set("Content-Type", "text/csv")
	w.Header().Set(
		"Content-Disposition",
		fmt.Sprintf(`attachment; filename="%s"`, filename),
	)

	writer := csv.NewWriter(w)

	if err := writer.Write([]string{
		"sheet_id",
		"student_id",
		"student_name",
		"correct",
		"incorrect",
		"unattempted",
		"marks",
		"total_questions",
	}); err != nil {
		http.Error(
			w,
			"Failed to write CSV header",
			http.StatusInternalServerError,
		)
		return
	}

	for _, result := range p.Results {
		if err := writer.Write([]string{
			result.SheetID,
			result.StudentID,
			result.StudentName,
			strconv.Itoa(result.Correct),
			strconv.Itoa(result.Incorrect),
			strconv.Itoa(result.Unattempted),
			strconv.Itoa(result.Marks),
			strconv.Itoa(result.TotalQuestions),
		}); err != nil {
			http.Error(
				w,
				"Failed to write CSV row",
				http.StatusInternalServerError,
			)
			return
		}
	}

	writer.Flush()

	if err := writer.Error(); err != nil {
		http.Error(
			w,
			"Failed to finalize CSV output",
			http.StatusInternalServerError,
		)
		return
	}

	fmt.Printf(
		"Exported results for project %s to CSV\n",
		p.ID,
	)
}
