import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from src.batch_main import run_batch
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def job():
    run_batch(Path("data/input.csv"), Path("output/result.csv"))


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # 動作確認用: 30秒ごとに実行(Quartzのsimple triggerに相当)
    scheduler.add_job(job, "interval", seconds=30)

    # 本番想定なら、こちらのように時刻指定もできる(Quartzのcron triggerに相当)
    # scheduler.add_job(job, "cron", hour=2, minute=0)

    logger.info("スケジューラー起動(Ctrl+Cで停止)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("スケジューラー停止")
