import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Reactの開発サーバー(Vite)からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/results")
def get_results():
    """バッチ処理結果をJSONで返す(Spring Bootの@GetMappingに相当)"""
    output_path = Path("output/result.csv")
    if not output_path.exists():
        return {"records": []}
    with output_path.open(encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    return {"records": records}
