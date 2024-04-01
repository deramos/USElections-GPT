import uvicorn
from fastapi import FastAPI
from api.routers import scrapers

app = FastAPI(version='1.0', description="US Election GPT APIs")
app.include_router(scrapers.router)


@app.get('/', tags=['home'])
def home():
    return {"name": "US Election GPT API", "version": "1.0"}


@app.get('/health', tags=['home'])
def health():
    return {"name": "US Elections API", 'status': 'running'}

