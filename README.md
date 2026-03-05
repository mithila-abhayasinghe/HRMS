# HRMS - Human Resource Management System

A modern, microservices-based Human Resource Management System built with Python FastAPI and React.

## Features

- **Employee Management** - Manage employee profiles, departments, and roles
- **Leave Management** - Request, approve, and track leave applications
- **Attendance Tracking** - Monitor employee attendance and work hours
- **Notifications** - Email-based notifications for important events
- **Audit Logging** - Complete audit trail of system activities
- **Compliance Monitoring** - Track compliance with HR policies
- **User Management** - Role-based access control and authentication
- **Asgardeo Integration** - OAuth2/OpenID Connect authentication

## Tech Stack

- **Backend:** Python FastAPI, SQLAlchemy ORM
- **Frontend:** React, Vite, Tailwind CSS
- **Database:** MySQL 8.0
- **Orchestration:** Docker & Docker Compose
- **Authentication:** Asgardeo (OAuth2/OIDC)

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd hr-management-system
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Wait for services to be healthy:**
   ```bash
   docker-compose ps
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Employee Service: http://localhost:8001
   - Leave Service: http://localhost:8002
   - Attendance Service: http://localhost:8003
   - Notification Service: http://localhost:8004
   - Audit Service: http://localhost:8005
   - Compliance Service: http://localhost:8006
   - User Service: http://localhost:8007

### Environment Configuration

All services are pre-configured in `docker-compose.yml`. Default credentials:
- **MySQL Root Password:** `password`
- **MySQL User:** `hrms_user`
- **MySQL Password:** `hrms_password`

Update these credentials in `docker-compose.yml` before production deployment.

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f <service-name>
# Example: docker-compose logs -f employee-service
```

## Project Structure

```
hr-management-system/
├── employee-management-service/    # Employee data management
├── leave-management-service/       # Leave request handling
├── attendance-management-service/  # Attendance tracking
├── notification-service/           # Email notifications
├── audit-service/                  # Audit logging
├── compliance-service/             # Compliance checks
├── user-management-service/        # User & auth management
├── hrms_frontend/                  # React frontend
├── docs/                           # Documentation
├── docker-compose.yml              # Docker orchestration
└── init.sql                        # Database initialization
```

## Documentation

Comprehensive documentation is available in the `/docs` directory:
- Service-specific docs in `docs/<service-name>/`
- Root documentation in `docs/root/`

## Development

Refer to the service-specific README files in `/docs`
for some documentation.
