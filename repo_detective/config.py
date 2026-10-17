import os
from dotenv import load_dotenv


def get_api_key():
    load_dotenv()
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")
    return key


def get_model_name():
    load_dotenv()
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")