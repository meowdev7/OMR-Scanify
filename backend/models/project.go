package models

type Project struct {
	ID            string    `json:"id"`
	Name          string    `json:"name"`
	QuestionCount int       `json:"question_count"`
	AnswerKey     []string  `json:"answer_key"`
	Students      []Student `json:"students"`
	Results       []Result  `json:"results"`
}
