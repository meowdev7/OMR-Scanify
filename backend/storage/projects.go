package storage

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"backend/models"
)

const projectsDirName = "projects"

func projectsDirPath() (string, error) {
	appDataDir, err := AppDataDir()
	if err != nil {
		return "", err
	}

	dir := filepath.Join(appDataDir, projectsDirName)

	if err := os.MkdirAll(dir, 0755); err != nil {
		return "", fmt.Errorf("failed to create projects directory: %w", err)
	}

	return dir, nil
}

func projectFilePath(id string) (string, error) {
	dir, err := projectsDirPath()
	if err != nil {
		return "", err
	}

	return filepath.Join(dir, id+".json"), nil
}

func SaveProjects(projects []models.Project) error {
	for _, project := range projects {
		filePath, err := projectFilePath(project.ID)
		if err != nil {
			return err
		}

		data, err := json.MarshalIndent(project, "", "    ")
		if err != nil {
			return fmt.Errorf("failed to encode project %s: %w", project.ID, err)
		}

		if err := os.WriteFile(filePath, data, 0644); err != nil {
			return fmt.Errorf("failed to write project %s: %w", project.ID, err)
		}
	}

	return nil
}

func DeleteProject(id string) error {
	filePath, err := projectFilePath(id)
	if err != nil {
		return err
	}

	if err := os.Remove(filePath); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to delete project %s: %w", id, err)
	}

	return nil
}

func LoadProjects() ([]models.Project, error) {
	dir, err := projectsDirPath()
	if err != nil {
		return nil, err
	}

	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, fmt.Errorf("failed to read projects directory: %w", err)
	}

	projects := make([]models.Project, 0)
	repairedTimestamp := false

	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}

		if filepath.Ext(entry.Name()) != ".json" {
			continue
		}

		filePath := filepath.Join(dir, entry.Name())

		data, err := os.ReadFile(filePath)
		if err != nil {
			return nil, fmt.Errorf(
				"failed to read project file %s: %w",
				entry.Name(),
				err,
			)
		}

		var project models.Project

		if err := json.Unmarshal(data, &project); err != nil {
			return nil, fmt.Errorf(
				"failed to decode project file %s: %w",
				entry.Name(),
				err,
			)
		}

		if project.CreatedAt.IsZero() {
			fileInfo, err := os.Stat(filePath)
			if err != nil {
				return nil, fmt.Errorf("failed to inspect project file %s: %w", entry.Name(), err)
			}
			project.CreatedAt = fileInfo.ModTime()
			repairedTimestamp = true
		}

		projects = append(projects, project)
	}

	if repairedTimestamp {
		if err := SaveProjects(projects); err != nil {
			return nil, err
		}
	}

	return projects, nil
}
