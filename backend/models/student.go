package models

type Student struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Class   string `json:"class"`
	Section string `json:"section"`
	RollNo  string `json:"roll_no"`
	SheetID string `json:"sheet_id"`
}
