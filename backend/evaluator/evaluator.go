package evaluator

func CheckAnswers(answers []*string, answerKey []string) []string {
	totalQuestions := len(answerKey)
	results := make([]string, totalQuestions)

	for i := 0; i < totalQuestions; i++ {
		if i >= len(answers) || answers[i] == nil {
			results[i] = "Unattempted"
		} else if *answers[i] == answerKey[i] {
			results[i] = "Correct"
		} else {
			results[i] = "Incorrect"
		}
	}

	return results
}

func CalculateMarks(results []string) int {
	marks := 0
	
	for _, result := range results {
		if result == "Correct" {
			marks++
		}
	}

	return marks
}
