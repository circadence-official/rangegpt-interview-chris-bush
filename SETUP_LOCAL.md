# Local Setup (without Docker)

If you prefer not to use Docker, follow these steps.

## Prerequisites

- Node.js 22
- Python 3.12
- PostgreSQL 16

## Database

1. Create the database:
   ```bash
   createdb interview
   ```

2. Set environment variables (or create a `.env` file in `backend/`):
   ```bash
   export POSTGRES_DB=interview
   export POSTGRES_USER=your_pg_user
   export POSTGRES_PASSWORD=your_pg_password
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export DJANGO_SECRET_KEY=dev-secret-key
   export DEBUG=True
   ```

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

The backend runs at [http://localhost:8000](http://localhost:8000).

## Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at [http://localhost:5173](http://localhost:5173).

**Note:** The Vite proxy expects the backend at `http://backend:8000` (Docker service name). For local development, update the proxy target in `vite.config.ts`:

```typescript
proxy: {
  "/api": {
    target: "http://localhost:8000",
    changeOrigin: true,
  },
},
```
