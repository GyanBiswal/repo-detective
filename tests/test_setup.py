import importlib
import pytest
from repo_detective import config


def test_missing_key_raises(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError):
        config.get_api_key()


def test_default_model(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    assert config.get_model_name() == "openai/gpt-oss-120b"


def test_libraries_installed():
    for name in ["dotenv", "langchain_groq", "langgraph", "langchain_mcp_adapters", "mcp", "git", "streamlit", "pydantic"]:
        importlib.import_module(name)