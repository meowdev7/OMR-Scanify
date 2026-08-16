package project

import "backend/models"

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