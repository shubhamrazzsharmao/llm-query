from fastapi import FastAPI, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import json
from datetime import datetime
import uvicorn
from dotenv import load_dotenv
import os
load_dotenv()

EMAIL = os.getenv("EMAIL")


with open("q-fastapi-llm-query.json") as f:
    data = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI LLM Query Service!"}

@app.get("/query")
def query(q: str = Query(...), response: Response = None):
    response.headers["X-Email"] = EMAIL

    q_lower = q.lower()
    answer: Union[str, int] = "Not Found"

    if "total sales of" in q_lower and "in" in q_lower:
        parts = q.split("total sales of")[1].split("in")
        product = parts[0].strip()
        city = parts[1].replace("?", "").strip()
        total = sum(entry["sales"] for entry in data if entry["product"] == product and entry["city"] == city)
        answer = total

    elif "how many sales reps" in q_lower and "in" in q_lower:
        region = q.split("in")[1].replace("?", "").strip()
        reps = set(entry["rep"] for entry in data if entry["region"] == region)
        answer = len(reps)

    elif "average sales for" in q_lower and "in" in q_lower:
        parts = q.split("average sales for")[1].split("in")
        product = parts[0].strip()
        region = parts[1].replace("?", "").strip()
        filtered = [entry["sales"] for entry in data if entry["product"] == product and entry["region"] == region]
        answer = round(sum(filtered) / len(filtered)) if filtered else 0

    elif "did" in q_lower and "make the highest sale in" in q_lower:
        rep = q.split("did")[1].split("make")[0].strip()
        city = q.split("in")[1].replace("?", "").strip()
        filtered = [entry for entry in data if entry["rep"] == rep and entry["city"] == city]
        if filtered:
            max_entry = max(filtered, key=lambda x: x["sales"])
            answer = max_entry["date"]
        else:
            answer = "N/A"

    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)