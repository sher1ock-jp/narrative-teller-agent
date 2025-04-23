import os
import uvicorn
import openai
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Directory containing this file
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Session DB URL (override via env var to use Cloud SQL)
SESSION_DB_URL = os.environ.get("SESSION_DB_URL", "sqlite:///./sessions.db")
# CORS allowed origins
ALLOWED_ORIGINS = ["*"]

# Create FastAPI app with ADK
app: FastAPI = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=True,
)

uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))