# Installation and Configuration Guide

## Technical Requirements

- Python 3.12+
- PostgreSQL 15+
- Docker and Docker Compose

## Installation Steps

1. Clone the repository:
bash
git clone [repository-url]
cd warehouse-management

2. Build and start the Docker containers:

```bash
docker-compose up --build
```

3. Access the application at http://localhost:5000

## Database Configuration

The application uses PostgreSQL with the following default settings:
Database - warehouse_db
Username - postgres
Password - postgres
Host - localhost
Port - 5432

These settings can be modified in the `docker-compose.yml` file.

## Environment Variables

The application uses the following environment variables (configured in docker-compose.yml):

```yaml
POSTGRES_DB: warehouse_db
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres
POSTGRES_HOST: db
POSTGRES_PORT: 5432
FLASK_APP: app.py
FLASK_ENV: development
JWT_SECRET_KEY: supersecretkey
```

## Initial Setup

The application automatically creates:
1. Default admin user
2. Test warehouse
3. Sample products

### Default Credentials

1. Administrator Account:
   - Username: admin
   - Password: admin123

2. Test Customer Account:
   - Username: testuser
   - Password: testpass

## Development Setup

1. Install Poetry (Python package manager):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Run in development mode:
```bash
poetry run flask run --debug
```

## Testing

Run the API tests:
```bash
python test_api.py
```

## Troubleshooting

1. Database Connection Issues:
   - Ensure PostgreSQL container is running: `docker ps`
   - Check logs: `docker-compose logs db`

2. Application Issues:
   - Check app logs: `docker-compose logs app`
   - Verify environment variables in docker-compose.yml
