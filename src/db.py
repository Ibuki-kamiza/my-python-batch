import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path("batch_history.db")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """テーブルが無ければ作成する(アプリ起動時に毎回呼んでOK)"""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at TEXT NOT NULL,
                success_count INTEGER NOT NULL DEFAULT 0,
                error_count INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'success'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs (id)
            )
            """
        )


def save_run(records: list[dict], error_count: int = 0) -> int:
    """バッチ実行結果を1回分、DBに保存する(Javaで言うrepository.save()に相当)"""
    run_at = datetime.now().isoformat(timespec="seconds")
    status = "success" if error_count == 0 else "partial_success"
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO runs (run_at, success_count, error_count, status) VALUES (?, ?, ?, ?)",
            (run_at, len(records), error_count, status),
        )
        run_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO results (run_id, date, name, category, amount) VALUES (?, ?, ?, ?, ?)",
            [(run_id, r["date"], r["name"], r["category"], r["amount"]) for r in records],
        )
    return run_id


def get_runs(date: str | None = None) -> list[dict]:
    """実行履歴の一覧を取得する(dateを指定すると実行日時がその日のものに絞り込む)"""
    with get_connection() as conn:
        query = "SELECT id, run_at, success_count, error_count, status FROM runs"
        params: tuple = ()
        if date:
            query += " WHERE run_at LIKE ?"
            params = (f"{date}%",)
        query += " ORDER BY run_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_run_detail(run_id: int) -> list[dict]:
    """特定の実行回の、個々のレコードを取得する"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT date, name, category, amount FROM results WHERE run_id = ?",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_summary() -> dict:
    """全実行をまたいだ集計データを取得する(合計金額・カテゴリー別・日別)"""
    with get_connection() as conn:
        total_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total_amount, COUNT(*) AS total_count FROM results"
        ).fetchone()

        category_rows = conn.execute(
            """
            SELECT category, SUM(amount) AS total_amount, COUNT(*) AS count
            FROM results
            GROUP BY category
            ORDER BY total_amount DESC
            """
        ).fetchall()

        daily_rows = conn.execute(
            """
            SELECT date, SUM(amount) AS total_amount, COUNT(*) AS count
            FROM results
            GROUP BY date
            ORDER BY date
            """
        ).fetchall()

        return {
            "total_amount": total_row["total_amount"],
            "total_count": total_row["total_count"],
            "by_category": [dict(row) for row in category_rows],
            "by_date": [dict(row) for row in daily_rows],
        }
