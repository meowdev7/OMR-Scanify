from pathlib import Path
import platformdirs
import json
import requests


APP_NAME = "OMR-Scanify"
API_URL = "http://127.0.0.1:8080/api/v1"


def get_projects_dir():
    config_dir = Path(platformdirs.user_config_dir(roaming=True))
    projects_dir = config_dir / APP_NAME / "projects"

    projects_dir.mkdir(parents=True, exist_ok=True)

    return projects_dir


def load_theme_preference():
    try:
        response = requests.get(f"{API_URL}/preferences", timeout=2)
        response.raise_for_status()
        theme = response.json().get("theme")
        return theme if theme in {"dark", "light", "system"} else "dark"
    except (requests.RequestException, ValueError):
        return "dark"


def save_theme_preference(theme):
    try:
        response = requests.put(
            f"{API_URL}/preferences",
            json={"theme": theme},
            timeout=2,
        )
        response.raise_for_status()
    except requests.RequestException:
        pass


def load_projects():
    response = requests.get(f"{API_URL}/projects", timeout=5)
    response.raise_for_status()
    return response.json()


def get_project(project_id):
    response = requests.get(f"{API_URL}/projects/{project_id}", timeout=5)
    response.raise_for_status()
    return response.json()


def update_answer_key(project_id, answer_key):
    response = requests.put(
        f"{API_URL}/projects/{project_id}/answer-key",
        json={"answer_key": answer_key},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def import_students(project_id, csv_text):
    response = requests.post(
        f"{API_URL}/projects/{project_id}/students/import",
        data=csv_text.encode("utf-8"),
        headers={"Content-Type": "text/csv"},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def load_results(project_id):
    response = requests.get(f"{API_URL}/projects/{project_id}/results", timeout=5)
    response.raise_for_status()
    return response.json()


def export_results(project_id, output_path):
    response = requests.get(f"{API_URL}/projects/{project_id}/results/export", timeout=10)
    response.raise_for_status()
    with open(output_path, "wb") as file:
        file.write(response.content)
    return output_path


def rename_project(project_id, name):
    response = requests.patch(
        f"{API_URL}/projects/{project_id}",
        json={"name": name},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def delete_project(project_id):
    response = requests.delete(f"{API_URL}/projects/{project_id}", timeout=5)
    response.raise_for_status()
    return response.json()


def update_project(project_id, name=None, question_count=None):
    payload = {}
    if name is not None:
        payload["name"] = name
    if question_count is not None:
        payload["question_count"] = question_count
    response = requests.patch(
        f"{API_URL}/projects/{project_id}",
        json=payload,
        timeout=5,
    )
    response.raise_for_status()
    return response.json()