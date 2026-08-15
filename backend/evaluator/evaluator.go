package evaluator

import (
	"backend/models"
)

func CheckAnswers(stu models.Student, key models.SolutionKey) []string {
	totalQuestions := len(key.CorrectAnswers)
	questions := make([]string, totalQuestions)

	for i := 0; i < totalQuestions; i++ {
		if i < len(stu.Answers) && stu.Answers[i] != nil {
			if *stu.Answers[i] == *key.CorrectAnswers[i] {
				questions[i] = "Correct"
			} else {
				questions[i] = "Incorrect"
			}
		} else {
			questions[i] = "Unattempted"
		}

	}

	return questions
}

func CalculateMarks(questions []string) int {
	marks := 0
	for _, result := range questions {
		if result == "Correct" {
			marks++
		}
	}
	return marks
}
