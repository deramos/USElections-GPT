from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('APScheduler')

SCRIPT_PATH = Path(__file__).parent / 'scripts'


def run_script(script_name):
    script_path = SCRIPT_PATH / script_name
    subprocess.run(['python3', str(script_path)], check=True)


def main():
    scheduler = BlockingScheduler()

    # Schedule news summary to run daily at 2:00 AM
    scheduler.add_job(
        lambda: run_script('news_summary.py'),
        CronTrigger.from_crontab('0 2 * * *'),
        id='news_summary',
        name='Run daily news summary'
    )

    # Schedule spider to run daily at 3:00 AM
    scheduler.add_job(
        lambda: run_script('run_spider.py'),
        CronTrigger.from_crontab('0 3 * * *'),
        id='run_spider',
        name='Run scraper spiders'
    )

    logger.info("Starting scheduler...")
    scheduler.start()


if __name__ == "__main__":
    main()