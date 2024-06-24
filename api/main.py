from fastapi import FastAPI
from api.routers import scrapers, chats, newsletter


app = FastAPI(version='1.0',  title='US Elections GPT API', description="US Election GPT APIs")
app.include_router(scrapers.router)
app.include_router(chats.router)
app.include_router(newsletter.router)


@app.get('/', tags=['home'])
def home():
    return {"name": "US Election GPT API", "version": "1.0"}


@app.get('/health', tags=['home'])
def health():
    return {"name": "US Elections API", 'status': 'running'}
