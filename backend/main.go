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

	mux.HandleFunc("POST /api/v1/projects/{id}/submissions", api.SubmissionHandler)

	fmt.Println("Server listening on :8080")

	err := http.ListenAndServe(":8080", mux)
	if err != nil {
		panic(err)
	}
}