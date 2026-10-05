import sys

import requests

query = " ".join(sys.argv[1:]) or "What is an AI agent and how is it different from RAG?"
resp = requests.post("http://127.0.0.1:8000/predict", json={"query": query}, timeout=600)
resp.raise_for_status()
print(resp.json()["output"])
