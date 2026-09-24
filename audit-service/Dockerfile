# syntax=docker/dockerfile:1

# Build Stage
FROM golang:1.27-alpine AS builder
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . ./
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /bin/audit-service ./cmd/server/

# Runtime
FROM alpine:latest
COPY --from=builder /bin/audit-service /audit-service
EXPOSE 8006
ENTRYPOINT ["/audit-service"]
