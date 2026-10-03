import csv
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.db import init_db, get_runs, get_run_detail, get_summary

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/results")
def get_results():
    """最新のバッチ結果(CSV)をJSONで返す"""
    output_path = Path("output/result.csv")
    if not output_path.exists():
        return {"records": []}
    with output_path.open(encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    return {"records": records}


@app.get("/api/runs")
def list_runs(date: str | None = Query(default=None, description="YYYY-MM-DD形式で実行日を絞り込み")):
    """実行履歴の一覧を返す"""
    return {"runs": get_runs(date)}


@app.get("/api/runs/{run_id}")
def run_detail(run_id: int):
    """特定の実行回の詳細(個々のレコード)を返す"""
    return {"records": get_run_detail(run_id)}


@app.get("/api/summary")
def summary():
    """全実行をまたいだ集計(合計金額・カテゴリー別・日別)を返す"""
    return get_summary()
