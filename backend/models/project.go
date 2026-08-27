package models

import "time"

type Project struct {
	ID            string    `json:"id"`
	Name          string    `json:"name"`
	CreatedAt     time.Time `json:"created_at"`
	QuestionCount int       `json:"question_count"`
	AnswerKey     []string  `json:"answer_key"`
	Students      []Student `json:"students"`
	Results       []Result  `json:"results"`
}
