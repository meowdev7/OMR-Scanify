package main

import (
	"backend/evaluator"
	"backend/models"
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	data, err := os.ReadFile("../test/sample.json")

	if err != nil {
		panic(err)
	}

	dat, err := os.ReadFile("../test/dummy_answer_key.json")

	if err != nil {
		panic(err)
	}

	var key models.SolutionKey
	var stu models.Student

	err = json.Unmarshal(data, &stu)

	if err != nil {
		panic(err)
	}

	err = json.Unmarshal(dat, &key)

	if err != nil {
		panic(err)
	}

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
	checkedAnswers := evaluator.CheckAnswers(stu, key)
	for i, result := range checkedAnswers {
		fmt.Printf("Answer %d: %s\n", i+1, result)
	}

	marks := evaluator.CalculateMarks(checkedAnswers)
	fmt.Printf("Total Marks: %d/%d\n", marks, len(key.CorrectAnswers))
}
