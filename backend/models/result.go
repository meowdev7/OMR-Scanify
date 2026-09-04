package models

type Result struct {
	SheetID            string            `json:"sheet_id"`
	StudentID          string            `json:"student_id"`
	StudentName        string            `json:"student_name"`
	Correct            int               `json:"correct"`
	Incorrect          int               `json:"incorrect"`
	Unattempted        int               `json:"unattempted"`
	Marks              int               `json:"marks"`
	TotalQuestions     int               `json:"total_questions"`
	StudentDetails     map[string]string `json:"student_details,omitempty"`
	IdentityStatus     string            `json:"identity_status,omitempty"`
	IdentityMismatches []string          `json:"identity_mismatches,omitempty"`
	Questions          []QuestionResult  `json:"questions,omitempty"`
}

type QuestionResult struct {
	Question      int     `json:"question"`
	CorrectAnswer string  `json:"correct_answer"`
	ScannedAnswer *string `json:"scanned_answer"`
	Status        string  `json:"status"`
	Confidence    float64 `json:"confidence"`
	Page          int     `json:"page"`
}
