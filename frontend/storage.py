from pathlib import Path
import platformdirs
import json


APP_NAME = "OMR-Scanify"


def get_projects_dir():
    config_dir = Path(platformdirs.user_config_dir(roaming=True))
    projects_dir = config_dir / APP_NAME / "projects"

    projects_dir.mkdir(parents=True, exist_ok=True)

    return projects_dir


def load_projects():
    projects_dir = get_projects_dir()
    projects = []

    for file_path in projects_dir.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                project = json.load(file)

            projects.append(project)

        except (json.JSONDecodeError, OSError) as e:
            print(f"Could not read {file_path.name}: {e}")

    return projects