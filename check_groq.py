from langchain_groq import ChatGroq
from repo_detective.config import get_api_key, get_model_name

llm = ChatGroq(model=get_model_name(), api_key=get_api_key())
reply = llm.invoke("Reply with exactly one word: pong")

print("Model:", get_model_name())
print("Reply:", reply.content)