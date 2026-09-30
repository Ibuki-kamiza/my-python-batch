import csv
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def read_input(input_path: Path) -> list[dict]:
    """CSVを読み込む処理(Spring BatchのItemReaderに相当)"""
    with input_path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def process_records(records: list[dict]) -> list[dict]:
    """データ加工処理(ItemProcessorに相当)"""
    processed = []
    for record in records:
        try:
            record["amount"] = int(record["amount"]) * 1.1  # 例: 消費税計算
            processed.append(record)
        except (KeyError, ValueError) as e:
            logger.warning(f"スキップ: {record} ({e})")
    return processed


def write_output(records: list[dict], output_path: Path) -> None:
    """結果を書き出す処理(ItemWriterに相当)"""
    if not records:
        logger.info("出力対象なし")
        return
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def run_batch(input_path: Path, output_path: Path) -> None:
    logger.info("バッチ開始")
    records = read_input(input_path)
    processed = process_records(records)
    write_output(processed, output_path)
    logger.info(f"バッチ終了: {len(processed)}件処理")


if __name__ == "__main__":
    run_batch(Path("data/input.csv"), Path("output/result.csv"))
