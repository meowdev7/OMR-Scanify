package models

type Student struct {
	StudentInfo struct {
		Name    string `json:"name"`
		Class   string `json:"class"`
		Section string `json:"section"`
		RollNo  string `json:"roll_no"`
	} `json:"student"`

	Answers []*string `json:"answers"`
}

type SolutionKey struct {
	CorrectAnswers []*string `json:"correct_answers"`
}
