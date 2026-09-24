package main

import (
	"fmt"
	"log/slog"
	"net/http"
)

const PORT string = ":8006"

func rootHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "audit-service\n")
	slog.Info("Root Request", "method", req.Method, "path", req.URL.Path)

}

func main() {

	slog.Info("starting audit-service", "port", PORT)

	http.HandleFunc("/", rootHandler)

	if err := http.ListenAndServe(PORT, nil); err != nil {
		slog.Error("server failed to start", "error", err)
	}

}
