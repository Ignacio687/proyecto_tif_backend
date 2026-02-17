# Servidor (backend) perteneciente al proyecto de Tesis “AICompanion”, para la cátedra de Trabajo Integrador Final (TIF), Universidad de Mendoza.

## Ignacio Chaves, legajo: 61.220

## Running locally with Docker Compose

Runs the API and MongoDB in containers:

1. Copy `.env.example` to `.env` and set your variables (at least `GEMINI_API_KEY`, `JWT_SECRET`, etc.).
2. From the project root:

   ```bash
   docker compose up --build
   ```

3. API: http://localhost:8001 (mapped from container 8000 so it doesn’t conflict with a local server on 8000). MongoDB: localhost:27017 (from host; from the app container use `mongodb:27017`).

To run in the background: `docker compose up -d --build`.

## API consumption (for another app)

- **Source of truth:** Use the **OpenAPI schema** exposed by the API:
  - Swagger UI: `http://localhost:8001/docs`
  - OpenAPI JSON: `http://localhost:8001/openapi.json`
  That gives you the exact contract: paths, methods, request/response schemas, required vs optional fields, and status codes. Use it for codegen, validation, or as context for another app.

- **Examples and manual testing:** The **Postman collection** (`postman/TIF_Backend_API.postman_collection.json`) is kept in sync with the API. It includes:
  - Auth: Google, register, login, verify-token, verify-email, resend-verification, password reset, refresh.
  - Assistant: POST `/api/v1/assistant` (body: `user_req`, optional `timezone`, `location`, `system_message`); GET `/api/v1/conversations` (query: `page`, `page_size`, optional `timezone`).
  Use it as reference for request bodies and headers (e.g. `Authorization: Bearer <access_token>` for protected routes). For another app’s implementation, prefer the OpenAPI schema; use the Postman collection for concrete examples.
