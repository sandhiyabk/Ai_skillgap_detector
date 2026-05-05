import os
from dotenv import load_dotenv

load_dotenv()

# Project Info
APP_NAME = "Interior Design Skill Gap Analyzer"
DOMAIN_NAME = "Interior Design"

# API Keys
HF_TOKEN = os.getenv("HF_TOKEN")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "HuggingFaceH4/zephyr-7b-beta")

# Groq API Keys (Primary)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# Database
DB_PATH = "data/sessions.db"

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Skill Categories for Radar Chart
SKILL_CATEGORIES = [
    "Design Software",
    "Client Communication",
    "Material Knowledge",
    "Space Planning",
    "Lighting Design",
    "Project Management"
]

# Style Config
THEME_COLOR = "#D4C4B5"  # Warm Neutral
SECONDARY_COLOR = "#5D5C5A" # Professional Grey
ACCENT_COLOR = "#8B7D6B" # Earthy Taupe
