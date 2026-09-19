# Task API with Supabase Authentication

A REST API built with FastAPI, PostgreSQL, Docker Compose, and Supabase Auth.

The project started as a CRUD Task API and was extended with secure user authentication using Supabase. Users can sign up, log in, receive JWT access tokens, access protected routes, and log out.

Protected endpoints verify Bearer tokens through Supabase before allowing access.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL 16
- Supabase Auth
- Supabase Python SDK
- psycopg
- Pydantic
- Docker
- Docker Compose
- Swagger UI

## Features

- Task CRUD API
- PostgreSQL database persistence
- User signup with Supabase Auth
- User login with access and refresh tokens
- JWT authentication
- Bearer token verification
- Reusable FastAPI authentication dependency
- Protected profile endpoint
- Protected dashboard endpoint
- Logout endpoint
- Public endpoint that requires no authentication
- Swagger UI with Bearer authentication
- Docker Compose setup
- Environment-variable based configuration

## Project Structure

```text
CRUD-Python/
├── main.py
├── repository.py
├── supabase_client.py
├── Dockerfile
├── docker-compose.yml
├── init.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Authentication Flow

The authentication flow uses Supabase as the Identity Provider.

```text
User
  |
  | email + password
  v
FastAPI
  |
  | signup / login request
  v
Supabase Auth
  |
  | JWT access token
  v
Client
  |
  | Authorization: Bearer <token>
  v
FastAPI Protected Route
  |
  | verify token
  v
Supabase Auth
  |
  | valid user
  v
Protected response
```

Passwords are not stored or hashed by this application. Supabase Auth handles password storage, hashing, authentication, and token generation.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ahmedsafdar3-cloud/CRUD-API.git
cd CRUD-API
```

### 2. Create a Supabase project

Create a project at Supabase and obtain:

- Project URL
- Anon/public API key

These values can be found in the Supabase project settings.

Do not use the `service_role` key for this project.

### 3. Create the environment file

Copy `.env.example` to `.env`.

The `.env` file should contain:

```text
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=8000
```

Replace the Supabase placeholders with your own project values.

The real `.env` file is ignored by Git and must never be committed.

## Run the Application

Start the API and PostgreSQL database with:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI is available at:

```text
http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/` | API information | No |
| GET | `/health` | Health check | No |
| POST | `/auth/signup` | Register a new user | No |
| POST | `/auth/login` | Log in and receive JWT tokens | No |
| POST | `/auth/logout` | Log out authenticated user | Yes |
| GET | `/public/info` | Public information | No |
| GET | `/protected/profile` | Return authenticated user profile | Yes |
| GET | `/protected/dashboard` | Example protected dashboard | Yes |
| GET | `/tasks` | Get all tasks | No |
| GET | `/tasks/{task_id}` | Get one task | No |
| POST | `/tasks` | Create a task | No |
| PUT | `/tasks/{task_id}` | Update a task | No |
| DELETE | `/tasks/{task_id}` | Delete a task | No |

## Sign Up

Request:

```http
POST /auth/signup
Content-Type: application/json
```

Example body:

```json
{
  "email": "user@example.com",
  "password": "ExamplePassword123!"
}
```

Successful signup returns:

```text
201 Created
```

Example response:

```json
{
  "message": "Signup successful",
  "user_id": "user-uuid"
}
```

Missing email or password returns:

```text
400 Bad Request
```

Depending on the Supabase project configuration, the user may need to confirm their email before logging in.

## Login

Request:

```http
POST /auth/login
Content-Type: application/json
```

Example body:

```json
{
  "email": "user@example.com",
  "password": "ExamplePassword123!"
}
```

A successful login returns an access token and refresh token:

```json
{
  "access_token": "<jwt-access-token>",
  "refresh_token": "<refresh-token>",
  "token_type": "bearer"
}
```

Invalid login credentials return:

```text
401 Unauthorized
```

## Protected Routes

Protected routes require an access token in the HTTP `Authorization` header.

The format is:

```text
Authorization: Bearer <access_token>
```

Example:

```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

A valid token returns:

```text
200 OK
```

and user information such as:

```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "created_at": "..."
}
```

A missing Bearer token returns:

```text
401 Unauthorized
```

Example:

```json
{
  "error": "Access token required"
}
```

An invalid, expired, or modified token also returns:

```text
401 Unauthorized
```

Example:

```json
{
  "error": "Invalid or expired token"
}
```

## Reusable Authentication Dependency

FastAPI uses a reusable authentication dependency for protected routes.

The dependency:

1. Reads the Bearer token.
2. Extracts the JWT.
3. Sends it to Supabase for verification.
4. Rejects invalid or expired tokens with `401`.
5. Returns the authenticated user when verification succeeds.

The same dependency is reused by:

```text
GET /protected/profile
GET /protected/dashboard
POST /auth/logout
```

This avoids duplicating authentication logic across routes.

## Swagger UI Authentication

FastAPI automatically provides Swagger UI at:

```text
http://localhost:8000/docs
```

Protected routes display a lock icon.

To test authentication through Swagger:

1. Call `POST /auth/login`.
2. Copy the returned `access_token`.
3. Click **Authorize** at the top of Swagger UI.
4. Paste the access token into the Bearer authentication field.
5. Click **Authorize**.
6. Run a protected endpoint such as `GET /protected/profile`.

Swagger automatically sends:

```text
Authorization: Bearer <token>
```

with protected requests.

## Swagger Screenshot

Add the Swagger UI screenshot here.

Example:

```markdown
![Swagger UI](docs/swagger-auth.png)
```

Create a `docs` folder in the repository and save the screenshot as:

```text
docs/swagger-auth.png
```

Then the image will appear in the README using:

```markdown
![Swagger UI](docs/swagger-auth.png)
```

## HTTP Status Codes

| Status | Meaning | Example |
|---|---|---|
| `200 OK` | Request completed successfully | Login or protected GET |
| `201 Created` | Resource/account created | Signup or task creation |
| `204 No Content` | Request succeeded with no response body | Logout or task deletion |
| `400 Bad Request` | Required input is missing or invalid | Empty signup fields |
| `401 Unauthorized` | Authentication is missing or invalid | Bad JWT or wrong login |
| `404 Not Found` | Requested resource does not exist | Missing task |

### 401 vs 403

`401 Unauthorized` means the API cannot authenticate the caller. For example, the access token is missing, malformed, invalid, or expired.

`403 Forbidden` means the caller has been authenticated successfully, but does not have permission to perform a particular action.

This project currently uses `401` for authentication failures. A role-based `403` authorization case can be added as a stretch feature.

## Task CRUD Examples

Get all tasks:

```bash
curl -i http://localhost:8000/tasks
```

Create a task:

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Finish authentication assignment","done":false}'
```

## Database Persistence

PostgreSQL runs inside a Docker container using a named Docker volume.

Database data survives:

```bash
docker compose down
docker compose up
```

The database volume is removed only when running:

```bash
docker compose down -v
```

## Database Initialization

`init.sql` creates the `tasks` table and inserts initial seed data when the PostgreSQL database is initialized for the first time.

## Security Notes

- Passwords are handled by Supabase Auth.
- Passwords are never stored directly by this application.
- JWT access tokens are verified before protected routes are executed.
- `.env` is excluded from Git.
- Real Supabase credentials must never be committed.
- `.env.example` contains placeholders only.
- Access tokens should not be shared or committed.
- The Supabase `service_role` key should never be exposed.

## Clean Clone

A new developer can run the project by cloning the repository:

```bash
git clone https://github.com/ahmedsafdar3-cloud/CRUD-API.git
cd CRUD-API
```

Create `.env` from `.env.example`, add valid Supabase credentials, then run:

```bash
docker compose up --build
```

No local PostgreSQL installation is required because PostgreSQL runs through Docker Compose.

## Assignment Progress

The project implements the required authentication stages:

- Stage 0 - Supabase and server setup
- Stage 1 - Signup and login
- Stage 2 - Public and protected routes
- Stage 3 - JWT verification
- Stage 4 - Reusable authentication dependency and logout
- Stage 5 - Swagger Bearer authentication
- Stage 6 - GitHub publishing and documentation

## Author

Ahmed Safdar