package storage

import (
	"os"
	"path/filepath"
)

const appName = "OMR-Scanify"

func AppDataDir() (string, error) {
	configDir, err := os.UserConfigDir() // better than handling appdata manually because this works cross-platform
	if err != nil {
		return "", err
	}

	appDataDir := filepath.Join(configDir, appName)

	if err := os.MkdirAll(appDataDir, 0755); err != nil {
		return "", err
	}

	return appDataDir, nil
}
