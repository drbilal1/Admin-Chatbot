# Admin Chatbot – User Management via Natural Language

A simple chatbot that lets an admin add, delete, and update user records using natural language commands instead of a traditional form-based UI.

## Tech Stack

- **Backend:** Django + Django REST Framework
- **Frontend:** Next.js (React)
- **AI:** Google Gemini API (gemini-3.6-flash) — converts natural language commands into structured actions
- **Database:** SQLite (Django default)

## Features

- Simple auto-login — enter any email that exists in the system to log in (no password required, per task requirements)
- Chat interface for managing users via plain English commands
- Supports three core actions:
  - **Add** a user: `"can you add the user john.smith@xyz.com with phone number +92332"`
  - **Delete** a user: `"can you remove the user john.smith@xyz.com"`
  - **Update** a user: `"can you update samanthas city to Cordoba"`

## How It Works

1. User logs in with an email that already exists in the database.
2. User types a natural language command in the chat.
3. The command is sent to the backend, where the Gemini API converts it into structured JSON (e.g. `{"action": "update", "name_lookup": "samantha", "field": "city", "value": "Cordoba"}`).
4. The backend validates and executes the corresponding database operation (add/delete/update) — the AI never touches the database directly, only produces intent, which the backend safely executes.
5. A confirmation message is sent back and displayed in the chat.

## Setup Instructions

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with: