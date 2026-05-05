import os
from dotenv import load_dotenv

load_dotenv()

# Project Info
APP_NAME = "Interior Design Skill Gap Analyzer"
DOMAIN_NAME = "Interior Design"

# Helper to get config from env or streamlit secrets
def get_config(key, default=None):
    # Try environment variable first
    val = os.getenv(key)
    if val:
        return val
    
    # Try streamlit secrets
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass
        
    return default

# API Keys
HF_TOKEN = get_config("HF_TOKEN")
MISTRAL_MODEL = get_config("MISTRAL_MODEL", "HuggingFaceH4/zephyr-7b-beta")

# Groq API Keys (Primary)
GROQ_API_KEY = get_config("GROQ_API_KEY")
LLM_MODEL = get_config("LLM_MODEL", "llama-3.3-70b-versatile")

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
