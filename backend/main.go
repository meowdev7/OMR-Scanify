package main

import (
	"backend/api"
	"fmt"
	"net/http"
)

/*
NOTE ->
// I've chosen to use the default HTTP multiplexer instead of fiber for the sake of learning and simplicity.
// Looking forward to implementing fiber in the future but as for now let's leave it as it is
*/

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/v1/projects", api.ListProjectsHandler)
	mux.HandleFunc("POST /api/v1/projects", api.CreateProjectHandler)

	mux.HandleFunc("GET /api/v1/projects/{id}", api.GetProjectHandler)
	mux.HandleFunc("PUT /api/v1/projects/{id}/answer-key", api.UpdateAnswerKeyHandler)
	mux.HandleFunc("POST /api/v1/projects/{id}/students/import", api.ImportStudentsHandler)
	mux.HandleFunc("POST /api/v1/projects/{id}/submissions", api.SubmissionHandler)
	mux.HandleFunc("GET /api/v1/projects/{id}/results", api.ListResultsHandler)
	mux.HandleFunc("GET /api/v1/projects/{id}/results/export", api.ExportResultsCSVHandler)

	fmt.Println("Server listening on :8080")

	if err := http.ListenAndServe(":8080", mux); err != nil {
		panic(err)
	}
}
