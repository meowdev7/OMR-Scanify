package main

import (
	"encoding/json"
	"fmt"
	"os"
)


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

func main() {
	data, err := os.ReadFile("../test/sample.json")

	if err != nil {
		panic(err)
	}

	dat, err := os.ReadFile("../test/dummy_answer_key.json")

	if err != nil {
		panic(err)
	}

	var key SolutionKey
	var stu Student

	err = json.Unmarshal(data, &stu)

	if err != nil {
		panic(err)
	}

	err = json.Unmarshal(dat, &key)

	if err != nil {
		panic(err)
	}
	// formattedJson, err := json.MarshalIndent(stu, "", " ")
	// if err != nil {
	// 	panic(err)
	// }
	// fmt.Printf("%s\n", formattedJson)
	// fmt.Println(stu)

	// replacing placeholders with the actual data

	for i, subkey := range key.CorrectAnswers {
		fmt.Printf("Correct Answer %d: %s\n", i+1, *subkey)
	}

	fmt.Printf("Student name : %v\n", stu.StudentInfo.Name)
	fmt.Printf("Student class and section : %v %v\n", stu.StudentInfo.Class, stu.StudentInfo.Section)
	fmt.Printf("Student Roll No. : %v\n", stu.StudentInfo.RollNo)

	for i, answer := range stu.Answers {
		if answer == nil {
			fmt.Printf("Answer %d: Unattempted\n", i+1) // start with index 1 instead of 0 (because answers start from 1, not 0)
		} else {
			fmt.Printf("Answer %d: %s\n", i+1, *answer) // same stuff here
		}
	}

	println("Checking answers...")
	checkedAnswers := checkAnswers(stu, key)
	for i, result := range checkedAnswers {
		fmt.Printf("Answer %d: %s\n", i+1, result)
	}

	marks := calculateMarks(checkedAnswers)
	fmt.Printf("Total Marks: %d/%d\n", marks, len(key.CorrectAnswers)) 
}


func checkAnswers (stu Student, key SolutionKey) []string {
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

func calculateMarks(questions []string) int {
	marks := 0
	for _, result := range questions {
		if result == "Correct" {
			marks++
		}
	}
	return marks
}