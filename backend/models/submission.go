package models

type Submission struct {
	SheetID string    `json:"sheet_id"`
	Answers []*string `json:"answers"`
}
