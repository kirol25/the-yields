import json
import re
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="The Yield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


@app.get("/api/years")
def get_years():
    ensure_data_dir()
    years = sorted(
        int(p.stem)
        for p in DATA_DIR.glob("*.json")
        if re.fullmatch(r"\d{4}", p.stem)
    )
    return years


@app.get("/api/data/{year}")
def get_data(year: int):
    ensure_data_dir()
    path = DATA_DIR / f"{year}.json"
    if not path.exists():
        return {"dividends": {}, "yields": {}}
    with open(path) as f:
        return json.load(f)


@app.put("/api/data/{year}")
def put_data(year: int, payload: dict):
    ensure_data_dir()
    path = DATA_DIR / f"{year}.json"
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return {"status": "ok"}
