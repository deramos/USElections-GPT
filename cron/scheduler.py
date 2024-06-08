from pathlib import Path
from crontab import CronTab

# Initialize a new cron
cron = CronTab(user=True)

SCRIPT_PATH = Path.joinpath(Path(__file__).parent, 'scripts')

# Define the first job
new_summary_job = cron.new(command=f'python3 {SCRIPT_PATH}/news_summary.py', comment='Run daily news summary')
new_summary_job.setall('0 2 * * *')

# Define the second job
spider_run_job = cron.new(command=f'python3 {SCRIPT_PATH}/run_spider.py', comment='Run scraper spiders')
spider_run_job.setall('0 2 * * *')

# Write the jobs to the crontab
cron.write()
