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
