package main

import (
	"backend/api"
	"backend/project"
	"backend/storage"
	"fmt"
	"net/http"
	"os"
	"strconv"
)

/*
NOTE ->
// I've chosen to use the default HTTP multiplexer instead of fiber for the sake of learning and simplicity.
// Looking forward to implementing fiber in the future but as for now let's leave it as it is
*/

func main() {
	if projects, err := storage.LoadProjects(); err == nil && len(projects) > 0 {
		project.Projects = projects
	}

	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/v1/preferences", api.PreferencesHandler)
	mux.HandleFunc("PUT /api/v1/preferences", api.PreferencesHandler)
	mux.HandleFunc("GET /api/v1/projects", api.ListProjectsHandler)
	mux.HandleFunc("POST /api/v1/projects", api.CreateProjectHandler)

	mux.HandleFunc("GET /api/v1/projects/{id}", api.GetProjectHandler)
	mux.HandleFunc("PATCH /api/v1/projects/{id}", api.RenameProjectHandler)
	mux.HandleFunc("DELETE /api/v1/projects/{id}", api.DeleteProjectHandler)
	mux.HandleFunc("PUT /api/v1/projects/{id}/answer-key", api.UpdateAnswerKeyHandler)
	mux.HandleFunc("DELETE /api/v1/projects/{id}/answer-key", api.DeleteAnswerKeyHandler)
	mux.HandleFunc("POST /api/v1/projects/{id}/students/import", api.ImportStudentsHandler)
	mux.HandleFunc("POST /api/v1/projects/{id}/submissions", api.SubmissionHandler)
	mux.HandleFunc("GET /api/v1/projects/{id}/results", api.ListResultsHandler)
	mux.HandleFunc("GET /api/v1/projects/{id}/results/export", api.ExportResultsCSVHandler)

	host := os.Getenv("OMR_SCANIFY_HOST")
	if host == "" {
		host = "127.0.0.1"
	}
	port := os.Getenv("OMR_SCANIFY_PORT")
	if parsedPort, err := strconv.Atoi(port); err != nil || parsedPort < 1 || parsedPort > 65535 {
		port = "8080"
	}
	address := host + ":" + port

	fmt.Printf("Server listening on %s\n", address)

	if err := http.ListenAndServe(address, mux); err != nil {
		panic(err)
	}
}
