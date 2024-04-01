from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import aiohttp
import asyncio
import logging
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class URLModel(BaseModel):
    url: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup cors for FastApi Application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

async def ping_url(url: str):
    logging.info(f"Pinging URL: {url}")
    status = 'red' # Default to red in case of an exception
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url) as response:
                status = 'green' if response.status == 200 else 'red'
                logging.info(f"Ping result for {url}: {status}")
    except Exception as e:
        logging.error(f"Error pinging {url}: {str(e)}")
    append_url_status_to_file(url, status)

def append_url_status_to_file(url: str, status: str):
    with open("url_status.txt", "a") as file:
        file.write(f"{url},{status}\n")

@app.get("/status/")
async def get_status(url: str):
    history = []
    with open("url_status.txt", "r") as file:
        for line in file:
            stored_url, stored_status = line.strip().split(',')
            if stored_url == url:
                history.append(stored_status)
    return {"history": history}

@app.post("/add_url")
async def add_url(url_data: URLModel, background_tasks: BackgroundTasks):
    await ping_url(url_data.url)
    return {"status": "success", "url": url_data.url}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_urls())

async def monitor_urls():
    logging.info("Starting URL monitoring task...")
    while True:
        try:
            with open("url_status.txt", "r") as file:
                urls = set(line.strip().split(',')[0] for line in file)
            for url in urls:
                await ping_url(url)
        except Exception as e:
            logging.error(f"Error in monitor_urls: {str(e)}")
        await asyncio.sleep(10)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

