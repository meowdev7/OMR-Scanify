package models

type Submission struct {
	SheetID            string            `json:"sheet_id"`
	Answers            []*string         `json:"answers"`
	Student            Student           `json:"student"`
	StudentDetails     map[string]string `json:"student_details,omitempty"`
	IdentityStatus     string            `json:"identity_status,omitempty"`
	IdentityMismatches []string          `json:"identity_mismatches,omitempty"`
	Scan               []Scan            `json:"scan"`
}

type Scan struct {
	Question   int     `json:"question"`
	Answer     *string `json:"answer"`
	Confidence float64 `json:"confidence"`
	Page       int     `json:"page"`
}
