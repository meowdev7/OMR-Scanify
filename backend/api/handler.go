package api

import (
	"fmt"
	"net/http"
)

func SubmissionHandler(w http.ResponseWriter, r *http.Request) {

	fmt.Fprintln(w, "Submission endpoint is alive")
	

}
