from fastapi import FastAPI, Header, HTTPException
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

API_KEY = os.environ.get("API_KEY")
MODEL_DIR = Path("/app/model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR)

app = FastAPI(title="VK LLM API")

@app.post("/v1/chat/completions")
def chat(prompt: str, x_api_key: str = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs, max_length=256)
    return {"completion": tokenizer.decode(output[0], skip_special_tokens=True)}
