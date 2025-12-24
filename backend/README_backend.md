# MindLens Backend

Small FastAPI backend to accept Habit Tracker submissions and save to Supabase.

## Run locally

1) Create and activate a virtual environment

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

2) Set environment variables

```bash
set SUPABASE_URL=your_supabase_url
set SUPABASE_ANON_KEY=your_supabase_anon_key
```

3) Start API

```bash
uvicorn app:app --reload
```

The endpoint will be at `http://localhost:8000/form/submit`.

## Endpoint

POST /form/submit

Body (JSON):
```json
{
  "user_id": "user-123",
  "sleep_hours": 6,
  "water_intake": 7,
  "screen_time": 4,
  "exercise": true,
  "social_interaction": 3,
  "meals": 2
}
```

Response (success):
```json
{
  "status": "saved",
  "data": { "timestamp": "...", "user_id": "...", "sleep_hours": 6, "water_intake": 7, "screen_time": 4, "exercise": true, "social_interaction": 3, "meals": 2 },
  "features": {
    "sleep_hours": 6,
    "water_intake": 7,
    "screen_time": 4,
    "exercise": 1,
    "social_interaction": 3,
    "meals": 2
  }
}
```

Response (error):
```json
{ "status": "error", "message": "...reason..." }
```

## Supabase schema (manual)

Create table `habit_forms`:

```sql
create table if not exists public.habit_forms (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  timestamp timestamptz default now(),
  sleep_hours int,
  water_intake int,
  screen_time int,
  exercise boolean,
  social_interaction int,
  meals int
);
```

Note: Ensure Row Level Security (RLS) and policies as needed for your environment.


