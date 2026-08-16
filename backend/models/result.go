package models

type Result struct {
	SheetID       string   `json:"sheet_id"`
	StudentID     string   `json:"student_id"`
	StudentName   string   `json:"student_name"`
	Correct       int      `json:"correct"`
	Incorrect     int      `json:"incorrect"`
	Unattempted   int      `json:"unattempted"`
	Marks         int      `json:"marks"`
	TotalQuestions int     `json:"total_questions"`
}

