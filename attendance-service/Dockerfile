# syntax=docker/dockerfile:1

# Build Stage
FROM golang:1.27-alpine AS builder
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . ./
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /bin/attendance-service ./cmd/server/

# Runtime
FROM alpine:latest
COPY --from=builder /bin/attendance-service /attendance-service
EXPOSE 8003
ENTRYPOINT ["/attendance-service"]
