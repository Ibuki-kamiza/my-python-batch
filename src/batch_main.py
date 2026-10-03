import csv
import logging
from datetime import datetime
from pathlib import Path

from src.db import init_db, save_run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def read_input(input_path: Path) -> list[dict]:
    """CSVを読み込む処理(Spring BatchのItemReaderに相当)"""
    with input_path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_record(record: dict) -> str | None:
    """1件分のバリデーション。問題があればエラー内容を返し、無ければNoneを返す"""
    if not record.get("name"):
        return "nameが空です"
    if not record.get("category"):
        return "categoryが空です"
    try:
        datetime.strptime(record.get("date", ""), "%Y-%m-%d")
    except ValueError:
        return f"dateの形式が不正です: {record.get('date')}"
    try:
        amount = int(record.get("amount", ""))
    except ValueError:
        return f"amountが数値ではありません: {record.get('amount')}"
    if amount <= 0:
        return f"amountは正の数である必要があります: {amount}"
    return None


def process_records(records: list[dict]) -> tuple[list[dict], int]:
    """データ加工処理(ItemProcessorに相当)。戻り値は(正常データ一覧, エラー件数)"""
    processed = []
    error_count = 0
    for record in records:
        error = validate_record(record)
        if error:
            logger.warning(f"スキップ: {record} ({error})")
            error_count += 1
            continue
        processed.append(
            {
                "date": record["date"],
                "name": record["name"],
                "category": record["category"],
                "amount": round(int(record["amount"]) * 1.1, 2),  # 消費税計算
            }
        )
    return processed, error_count


def write_output(records: list[dict], output_path: Path) -> None:
    """結果を書き出す処理(最新スナップショット用のCSV。ItemWriterに相当)"""
    if not records:
        logger.info("出力対象なし")
        return
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def run_batch(input_path: Path, output_path: Path) -> None:
    logger.info("バッチ開始")
    init_db()
    records = read_input(input_path)
    processed, error_count = process_records(records)
    write_output(processed, output_path)
    run_id = save_run(processed, error_count)
    logger.info(
        f"バッチ終了: 成功{len(processed)}件 / エラー{error_count}件(run_id={run_id})"
    )


if __name__ == "__main__":
    run_batch(Path("data/input.csv"), Path("output/result.csv"))
