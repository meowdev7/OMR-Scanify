package storage

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"backend/models"
)

const projectsFileName = "projects.json"

func projectsFilePath() (string, error) {
	appDataDir, err := AppDataDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(appDataDir, projectsFileName), nil
}

func SaveProjects(projects []models.Project) error {
	filePath, err := projectsFilePath()
	if err != nil {
		return err
	}
	data, err := json.MarshalIndent(projects, "", "    ")
	if err != nil {
		return fmt.Errorf("failed to encode projects: %w", err)
	}

	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return fmt.Errorf("failed to write projects: %w", err)
	}

	return nil
}

func LoadProjects() ([]models.Project, error) {
	filePath, err := projectsFilePath()
	if err != nil {
		return nil, err
	}

	data, err := os.ReadFile(filePath)
	if os.IsNotExist(err) { // ts is for a first-time user
		return []models.Project{}, nil
	}

	if err != nil {
		return nil, fmt.Errorf("failed to read projects: %w", err)
	}

	var projects []models.Project

	if err := json.Unmarshal(data, &projects); err != nil {
		return nil, fmt.Errorf("failed to decode projects: %w", err)
	}

	return projects, nil
}
