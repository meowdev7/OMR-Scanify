package utils

import "net/http"

func CheckError(e error) {
	if e != nil {
		panic(e)
	}
}

func CheckHTTPError(w http.ResponseWriter, e error, message string, statusCode int) {
	if e != nil {
		panic(e)
	}
	http.Error(w, message, statusCode)
}