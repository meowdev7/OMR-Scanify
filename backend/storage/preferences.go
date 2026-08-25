package storage

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type Preferences struct {
	Theme string `json:"theme"`
}

func preferencesFilePath() (string, error) {
	appDataDir, err := AppDataDir()
	if err != nil {
		return "", err
	}

	return filepath.Join(appDataDir, "preferences.json"), nil
}

func LoadPreferences() (Preferences, error) {
	filePath, err := preferencesFilePath()
	if err != nil {
		return Preferences{}, err
	}

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			return Preferences{Theme: "dark"}, nil
		}
		return Preferences{}, fmt.Errorf("failed to read preferences: %w", err)
	}

	var preferences Preferences
	if err := json.Unmarshal(data, &preferences); err != nil {
		return Preferences{}, fmt.Errorf("failed to decode preferences: %w", err)
	}

	if preferences.Theme == "" {
		preferences.Theme = "dark"
	}

	return preferences, nil
}

func SavePreferences(preferences Preferences) error {
	filePath, err := preferencesFilePath()
	if err != nil {
		return err
	}

	data, err := json.MarshalIndent(preferences, "", "    ")
	if err != nil {
		return fmt.Errorf("failed to encode preferences: %w", err)
	}

	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return fmt.Errorf("failed to write preferences: %w", err)
	}

	return nil
}
