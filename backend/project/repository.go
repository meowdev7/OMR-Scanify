package project

import (
	"backend/models"
	"fmt"
	"strings"
)

var Projects = []models.Project{
	{
		ID:            "PHY-001",
		Name:          "Physics Unit Test 1",
		QuestionCount: 8,
		AnswerKey: []string{
			"A",
			"B",
			"C",
			"A",
			"D",
			"A",
			"C",
			"D",
		},
		Students: []models.Student{
			{
				ID:      "STU-001",
				Name:    "Example Student",
				Class:   "XI",
				Section: "A1",
				RollNo:  "17",
				SheetID: "PHY-001-S0001",
			},
			{
				ID:      "STU-002",
				Name:    "Another Student",
				Class:   "XI",
				Section: "A1",
				RollNo:  "18",
				SheetID: "PHY-001-S0002",
			},
		},
		Results: []models.Result{},
	},
}

func GetProjectByID(id string) *models.Project {
	for i := range Projects {
		if Projects[i].ID == id {
			return &Projects[i]
		}
	}
	return nil
}

func GetStudentBySheetID(p *models.Project, sheetID string) *models.Student {
	for i := range p.Students {
		if p.Students[i].SheetID == sheetID {
			return &p.Students[i]
		}
	}
	return nil
}

func CreateProject(name string, questionCount int) *models.Project {
	id := generateProjectID(name)

	p := models.Project{
		ID:            id,
		Name:          name,
		QuestionCount: questionCount,
		AnswerKey:     []string{},
		Students:      []models.Student{},
		Results:       []models.Result{},
	}

	Projects = append(Projects, p)

	return &Projects[len(Projects)-1]
}

func AddResultToProject(p *models.Project, r models.Result) {
	for i := range p.Results {
		if p.Results[i].SheetID == r.SheetID {
			p.Results[i] = r
			return
		}
	}

	p.Results = append(p.Results, r)
}

func generateProjectID(name string) string {
	name = strings.TrimSpace(name)

	if name == "" {
		return "PROJ-001"
	}

	prefix := strings.ToUpper(name)

	if len(prefix) > 4 {
		prefix = prefix[:4]
	}

	maxNumber := 0

	for _, p := range Projects {
		parts := strings.SplitN(p.ID, "-", 2)

		if len(parts) != 2 || parts[0] != prefix {
			continue
		}

		var number int
		if _, err := fmt.Sscanf(parts[1], "%d", &number); err != nil {
			continue
		}

		if number > maxNumber {
			maxNumber = number
		}
	}

	return fmt.Sprintf("%s-%03d", prefix, maxNumber+1)
}
