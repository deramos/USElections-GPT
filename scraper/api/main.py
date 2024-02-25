from fastapi import FastAPI
from scraper.scraper.spiders import CNNSpider

app = FastAPI(version=1.0, description="Scraper APIs")


@app.get('/')
def home():
    return {"message": "Scraper API", "version": "1.0"}


@app.get('/health')
def health():
    return {'status': 'running'}


@app.get('/scrapers/{scraper_name}/start')
def start_scraper(scraper_name: )