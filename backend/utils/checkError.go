package utils

import "net/http"

func CheckError(e error) {
	if e != nil {
		panic(e)
	}
}

func CheckHTTPError(
	w http.ResponseWriter,
	err error,
	message string,
	status int,
) bool {
	if err != nil {
		http.Error(w, message, status)
		return true
	}

	return false
}