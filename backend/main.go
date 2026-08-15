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

	Answers []string `json:"answers"`
}

func main() {
	data, err := os.ReadFile("../test/sample.json")

	if err != nil {
		panic(err)
	}

	var stu Student
	err = json.Unmarshal(data, &stu)
	if err != nil {
		panic(err)
	}
	formattedJson, err := json.MarshalIndent(stu, "", " ")
	if err != nil {
		panic(err)
	}
	fmt.Printf("%s\n", formattedJson)
}
